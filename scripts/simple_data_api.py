#!/usr/bin/env python3
"""Simplified Data Explorer API"""

import json
import hashlib
import base64
import math
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

def sanitize_for_json(obj):
    """Recursively sanitize object for JSON serialization."""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    else:
        return obj

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row
import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

# Initialize FastAPI app
app = FastAPI(title="Simple Data Explorer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
SUPABASE_DSN = os.getenv("POSTGRES_DSN")
if not SUPABASE_DSN:
    raise ValueError("POSTGRES_DSN environment variable is required")

# Pydantic models
class InputRecord(BaseModel):
    index: int
    block_number: int
    timestamp: str
    msg_sender: str
    payload: Dict[str, Any]
    status: str

class DecryptRequest(BaseModel):
    index: int
    device_id: str

class DecryptBatchRequest(BaseModel):
    records: List[InputRecord]

# Utility functions
def b64url_decode(data: str) -> bytes:
    """Base64-URL decode with correct padding."""
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def derive_key(device_id: str, tag: str) -> bytes:
    return hashlib.sha256(f"{device_id}{tag}".encode()).digest()

def derive_nonce(device_id: str, tag: str, counter: int) -> bytes:
    return hashlib.sha256(f"{device_id}{tag}{counter}".encode()).digest()[:12]

def decrypt_payload(device_id: str, counter: int, encrypted_b64: str) -> str:
    """Perform Stage-2 (ChaCha20-Poly1305) then Stage-1 (AES-256-GCM) decryption."""
    stage2_cipher = ChaCha20Poly1305(derive_key(device_id, "stage2_key"))
    stage2_nonce = derive_nonce(device_id, "stage2_nonce", counter)
    stage1_bytes = stage2_cipher.decrypt(stage2_nonce, base64.b64decode(encrypted_b64), None)

    stage1_cipher = AESGCM(derive_key(device_id, "stage1_key"))
    stage1_nonce = derive_nonce(device_id, "stage1_nonce", counter)
    plaintext = stage1_cipher.decrypt(stage1_nonce, stage1_bytes, None)
    return plaintext.decode()

def safe_float_convert(value, default=None):
    """Safely convert value to float, handling NaN and Infinity."""
    try:
        if value is None:
            return default
        val = float(value)
        if math.isnan(val) or math.isinf(val):
            return default
        return val
    except (ValueError, TypeError):
        return default

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        with psycopg.connect(SUPABASE_DSN) as conn:
            conn.execute("SELECT 1")
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@app.get("/api/inputs")
async def fetch_inputs(
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    limit: int = Query(50, description="Maximum number of records"),
    block_number_min: Optional[int] = Query(None, description="Minimum block number")
):
    """Fetch raw encrypted inputs from Supabase."""
    try:
        with psycopg.connect(SUPABASE_DSN, row_factory=dict_row) as conn:
            # Build query
            where_clauses = []
            params = []
            
            if block_number_min:
                where_clauses.append("block_number >= %s")
                params.append(block_number_min)
            
            where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            query = f"""
                SELECT 
                    index,
                    block_number,
                    timestamp,
                    msg_sender,
                    payload,
                    status
                FROM inputs
                {where_sql}
                ORDER BY index DESC
                LIMIT %s
            """
            params.append(limit)
            
            rows = conn.execute(query, params)
            records = rows.fetchall()
            
            # Parse payload data
            parsed_records = []
            for record in records:
                try:
                    # Handle payload parsing
                    payload_data = record['payload']
                    if isinstance(payload_data, bytes):
                        payload_str = payload_data.decode().replace("NaN", "null")
                        payload_json = json.loads(payload_str)
                        outer_json = payload_json  # Direct format
                    else:
                        outer_json = payload_data
                    
                    # Filter by device type if specified
                    if device_type and device_type != 'all':
                        device_id = outer_json.get('device_id', '')
                        if device_type not in device_id:
                            continue
                    
                    parsed_records.append({
                        "index": record['index'],
                        "block_number": record['block_number'],
                        "timestamp": record['timestamp'].isoformat() if record['timestamp'] else None,
                        "msg_sender": record['msg_sender'].hex() if isinstance(record['msg_sender'], bytes) else str(record['msg_sender']),
                        "payload": outer_json,
                        "status": str(record['status'])
                    })
                    
                except Exception as e:
                    print(f"Error parsing record {record.get('index', 'unknown')}: {e}")
                    continue
            
            return {
                "records": parsed_records,
                "total": len(parsed_records),
                "filtered_by": device_type
            }
            
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/decrypt")
async def decrypt_single_input(request: DecryptRequest):
    """Decrypt a single input by index and device ID."""
    try:
        with psycopg.connect(SUPABASE_DSN, row_factory=dict_row) as conn:
            query = "SELECT payload FROM inputs WHERE index = %s LIMIT 1"
            row = conn.execute(query, (request.index,))
            record = row.fetchone()
            
            if not record:
                raise HTTPException(status_code=404, detail=f"Input {request.index} not found")
            
            # Parse payload
            payload_data = record['payload']
            if isinstance(payload_data, bytes):
                payload_str = payload_data.decode().replace("NaN", "null")
                payload_json = json.loads(payload_str)
                outer_json = payload_json
            else:
                outer_json = payload_data
            
            # Extract JWS token
            jws = outer_json.get('encrypted_payload')
            if not jws:
                raise HTTPException(status_code=400, detail="No encrypted_payload found in input")
            
            # Decode JWS (without signature verification for demo)
            try:
                header_b64, payload_b64, _signature = jws.split(".")
                claims = json.loads(b64url_decode(payload_b64))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid JWS format: {str(e)}")
            
            # Extract encrypted data and counter
            enc_field = claims.get("encrypted_data")
            counter = claims.get("counter", 0)
            
            if not enc_field:
                raise HTTPException(status_code=400, detail="No encrypted_data in JWS payload")
            
            # Decrypt
            clear_text = decrypt_payload(request.device_id, counter, enc_field)
            sensor_data = json.loads(clear_text)
            # Sanitize the decrypted data to handle NaN values
            sensor_data = sanitize_for_json(sensor_data)
            
            result = {
                "device_id": request.device_id,
                "index": request.index,
                "decrypted_data": sensor_data,
                "jws_claims": claims
            }
            return sanitize_for_json(result)
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Decryption error: {e}")
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")

@app.post("/api/decrypt-batch")
async def decrypt_batch_inputs(request: DecryptBatchRequest):
    """Decrypt multiple inputs at once."""
    try:
        decrypted_results = []
        
        for record in request.records:
            try:
                # Extract device ID from payload
                device_id = record.payload.get('device_id')
                if not device_id:
                    continue
                
                # Extract JWS token
                jws = record.payload.get('encrypted_payload')
                if not jws:
                    continue
                
                # Decode JWS
                header_b64, payload_b64, _signature = jws.split(".")
                claims = json.loads(b64url_decode(payload_b64))
                
                # Extract encrypted data and counter
                enc_field = claims.get("encrypted_data")
                counter = claims.get("counter", 0)
                
                if not enc_field:
                    continue
                
                # Decrypt
                clear_text = decrypt_payload(device_id, counter, enc_field)
                sensor_data = json.loads(clear_text)
                # Sanitize the decrypted data to handle NaN values
                sensor_data = sanitize_for_json(sensor_data)
                
                # Extract domain
                domain = 'environmental' if 'env-' in device_id else \
                        'health' if 'health-tracker-' in device_id else \
                        'retail' if 'retail-' in device_id else \
                        'network' if 'cell-tower-' in device_id else \
                        'weather' if 'weather-station-' in device_id else \
                        'agricultural' if 'agri-' in device_id else 'unknown'
                
                # Build standardized response
                decrypted_payload = {
                    "device_id": device_id,
                    "timestamp": sensor_data.get('timestamp', 0),
                    "domain": domain,
                    "sensor_type": sensor_data.get('sensor_type', domain),
                    "privacy_metadata": sensor_data.get('privacy_metadata', {
                        "pii_removed": True,
                        "location_anonymized": True,
                        "encryption_ready": True,
                        "privacy_score": 100
                    })
                }
                
                # Add domain-specific fields
                if domain == 'environmental':
                    decrypted_payload.update({
                        "temperature": safe_float_convert(sensor_data.get('temperature')),
                        "humidity": safe_float_convert(sensor_data.get('humidity')),
                        "air_quality_index": sensor_data.get('air_quality_index')
                    })
                elif domain == 'health':
                    decrypted_payload.update({
                        "temperature": safe_float_convert(sensor_data.get('temperature'))
                    })
                elif domain == 'retail':
                    decrypted_payload.update({
                        "transaction_value": safe_float_convert(sensor_data.get('transaction_value')),
                        "kc_neighborhood": sensor_data.get('kc_neighborhood'),
                        "anonymized_customer_count": sensor_data.get('anonymized_customer_count')
                    })
                elif domain == 'network':
                    decrypted_payload.update({
                        "signal_strength_dbm": safe_float_convert(sensor_data.get('signal_strength_dbm')),
                        "latency_ms": safe_float_convert(sensor_data.get('latency_ms')),
                        "bandwidth_mbps": safe_float_convert(sensor_data.get('bandwidth_mbps'))
                    })
                elif domain == 'weather':
                    decrypted_payload.update({
                        "temperature": safe_float_convert(sensor_data.get('temperature_celsius')),
                        "humidity": safe_float_convert(sensor_data.get('humidity_percent')),
                        "pressure_hpa": safe_float_convert(sensor_data.get('pressure_hpa'))
                    })
                
                decrypted_results.append(decrypted_payload)
                
            except Exception as e:
                print(f"Error decrypting record {record.index}: {e}")
                continue
        
        result = {
            "decrypted_data": decrypted_results,
            "total_decrypted": len(decrypted_results),
            "total_attempted": len(request.records)
        }
        return sanitize_for_json(result)
        
    except Exception as e:
        print(f"Batch decryption error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch decryption failed: {str(e)}")

if __name__ == "__main__":
    import os
    
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '8091'))
    
    print(f"Starting Simple Data Explorer API on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )