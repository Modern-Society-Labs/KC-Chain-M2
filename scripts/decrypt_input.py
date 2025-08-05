#!/usr/bin/env python3
"""
Decrypt a single Cartesi InputBox payload stored in Supabase.
-----------------------------------------------------------------
Usage (environment variables or CLI flags):

    python decrypt_input.py \
        --dsn postgresql://user:pass@host:port/dbname \
        --index 23978 \
        --device-id did:lcore:env-102-air

The script:
1. Pulls `payload` for the given `index` from the `inputs` table.
2. Re-assembles the Buffer (array of ints) into bytes.
3. Decodes the outer JSON that contains `encrypted_payload` (a JWS token).
4. Decodes the JWS payload without verifying signature.
5. If the payload contains an `encrypted_data` field, performs the
   dual-layer decryption (AES-256-GCM, then XChaCha20-Poly1305) using
   deterministic keys derived from the `device_id` and `counter`.
6. Prints the resulting clear-text sensor reading.
"""
import argparse
import base64
import hashlib
import json
import os
import sys
from typing import Any, Dict

import psycopg
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def b64url_decode(data: str) -> bytes:
    """Base64-URL decode with correct padding."""
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def derive_key(device_id: str, tag: str) -> bytes:
    return hashlib.sha256(f"{device_id}{tag}".encode()).digest()


def derive_nonce(device_id: str, tag: str, counter: int) -> bytes:
    return hashlib.sha256(f"{device_id}{tag}{counter}".encode()).digest()[:12]


def decrypt_payload(device_id: str, counter: int, encrypted_b64: str) -> str:
    """Perform Stage-2 (XChaCha20-Poly1305) then Stage-1 (AES-256-GCM) decryption."""
    stage2_cipher = ChaCha20Poly1305(derive_key(device_id, "stage2_key"))
    stage2_nonce  = derive_nonce(device_id, "stage2_nonce", counter)
    stage1_bytes  = stage2_cipher.decrypt(stage2_nonce, base64.b64decode(encrypted_b64), None)

    stage1_cipher = AESGCM(derive_key(device_id, "stage1_key"))
    stage1_nonce  = derive_nonce(device_id, "stage1_nonce", counter)
    plaintext     = stage1_cipher.decrypt(stage1_nonce, stage1_bytes, None)
    return plaintext.decode()


# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Decrypt a Cartesi input payload")
    DEFAULT_DSN = os.getenv("POSTGRES_DSN")
    if not DEFAULT_DSN:
        print("Error: POSTGRES_DSN environment variable is required")
        sys.exit(1)
    parser.add_argument("--dsn", help="PostgreSQL DSN", required=False, default=DEFAULT_DSN)
    parser.add_argument("--index", type=int, help="Input index in `inputs` table", required=True)
    parser.add_argument("--device-id", help="Device ID (did:lcore:...) used to derive keys", required=True)

    args = parser.parse_args()
    if not args.dsn:
        sys.exit("Error: Provide a Supabase DSN via --dsn or POSTGRES_DSN env var.")

    # Connect & fetch payload
    with psycopg.connect(args.dsn) as conn:
        row = conn.execute("SELECT payload FROM inputs WHERE index = %s LIMIT 1", (args.index,)).fetchone()
        if row is None:
            sys.exit(f"Input index {args.index} not found.")
        payload_bytea: bytes = row[0]

    # Convert bytea to utf-8 string, fix NaN tokens, load as json
    payload_json: Dict[str, Any] = json.loads(payload_bytea.decode().replace("NaN", "null"))

    # Handle two cases:
    # 1) Supabase stores a Buffer wrapper {"type":"Buffer","data":[...]}
    # 2) It already stores the plain outer JSON
    if payload_json.get("type") == "Buffer" and "data" in payload_json:
        data_bytes = bytes(int(b) for b in payload_json["data"])
        outer_json = json.loads(data_bytes.decode())
    else:
        outer_json = payload_json  # already plain JSON

    print("Outer JSON (from InputBox):")
    print(json.dumps(outer_json, indent=2))

    jws = outer_json.get("encrypted_payload") or outer_json.get("encryptedPayload")
    if not jws:
        sys.exit("No `encrypted_payload` field present – nothing to decrypt")

    try:
        header_b64, payload_b64, _signature = jws.split(".")
    except ValueError:
        sys.exit("Malformed JWS token")

    header  = json.loads(b64url_decode(header_b64))
    claims  = json.loads(b64url_decode(payload_b64))

    print("\nJWS header:")
    print(json.dumps(header,  indent=2))
    print("\nJWS payload (claims):")
    print(json.dumps(claims, indent=2))

    enc_field = claims.get("encrypted_data") or claims.get("encrypted_payload")
    counter   = claims.get("counter", 0)

    if enc_field:
        print("\nPerforming dual-stage decryption …")
        clear_text = decrypt_payload(args.device_id, counter, enc_field)
        print("\nDecrypted sensor payload:")
        print(clear_text)
    else:
        print("\nNo encrypted_data field found – claims already in clear-text.")


if __name__ == "__main__":
    main()
