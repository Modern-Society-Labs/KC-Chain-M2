#!/usr/bin/env python3
"""
Device Registration Script using Cast Commands
Sends device registration data via Cartesi input box
"""

import json
import pandas as pd
import subprocess
import logging
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import hashlib
import base64
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CastDeviceRegistrator:
    """Register devices using cast commands to Cartesi input box"""
    
    def __init__(self, 
                 input_box_address: str = "0xC1f612D9ad2270e31BF41fAdBb92f79B63649133",
                 dapp_address: str = "0xB7B462b81A10A24e1976C9029Ef8FfBdCFc1a96a",
                 rpc_url: str = "https://rpc.devnet.alchemy.com/7eade438-d743-4dc5-ac64-3480de391200",
                 private_key: str = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"):
        self.input_box_address = input_box_address
        self.dapp_address = dapp_address
        self.rpc_url = rpc_url
        self.private_key = private_key
    
    def derive_device_private_key(self, device_id: str) -> ec.EllipticCurvePrivateKey:
        """Derive ECDSA private key from device ID (same as simulation service)"""
        seed = hashlib.sha256(f"{device_id}_device_key".encode()).digest()
        
        # P-256 curve order (n)
        # This is the same value used in the simulation service
        p256_order = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
        
        private_value = int.from_bytes(seed, byteorder='big') % p256_order
        if private_value == 0:
            private_value = 1  # Ensure non-zero private key
            
        private_key = ec.derive_private_key(
            private_value,
            ec.SECP256R1(),
            default_backend()
        )
        return private_key
    
    def create_did_document(self, device_id: str) -> dict:
        """Create a DID document with public key for the device"""
        private_key = self.derive_device_private_key(device_id)
        public_key = private_key.public_key()
        
        # Get public key in JWK format for DID document
        public_key_numbers = public_key.public_numbers()
        
        # Convert coordinates to base64url (32 bytes each for P-256)
        x_bytes = public_key_numbers.x.to_bytes(32, byteorder='big')
        y_bytes = public_key_numbers.y.to_bytes(32, byteorder='big')
        
        x_b64 = base64.urlsafe_b64encode(x_bytes).decode('utf-8').rstrip('=')
        y_b64 = base64.urlsafe_b64encode(y_bytes).decode('utf-8').rstrip('=')
        
        # Create DID document following W3C DID Core spec
        did_document = {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/jws-2020/v1"
            ],
            "id": device_id,
            "verificationMethod": [{
                "id": f"{device_id}#key-1",
                "type": "JsonWebKey2020",
                "controller": device_id,
                "publicKeyJwk": {
                    "kty": "EC",
                    "crv": "P-256",
                    "x": x_b64,
                    "y": y_b64,
                    "use": "sig",
                    "alg": "ES256"
                }
            }],
            "authentication": [f"{device_id}#key-1"],
            "assertionMethod": [f"{device_id}#key-1"]
        }
        
        return did_document
    
    def create_registration_command(self, device_id: str, wallet_address: str) -> dict:
        """Create device registration command for Cartesi"""
        did_doc = self.create_did_document(device_id)
        
        # Create registration command that the lcore-node expects
        command = {
            "type": "register_device",
            "device_id": device_id,
            "wallet_address": wallet_address,
            "did_document": json.dumps(did_doc),
            "public_key": did_doc["verificationMethod"][0]["publicKeyJwk"],
            "device_type": "iot_sensor",
            "metadata": {
                "registered_via": "cast_script",
                "registration_timestamp": int(time.time())
            }
        }
        
        return command
    
    def send_cast_command(self, command: dict) -> bool:
        """Send command via cast to Cartesi input box"""
        try:
            # Convert command to JSON string
            command_json = json.dumps(command, separators=(',', ':'))
            
            # Convert to hex for cast
            command_hex = command_json.encode('utf-8').hex()
            
            logger.info(f"🚀 Sending cast command for device: {command['device_id']}")
            logger.debug(f"Command: {command_json[:100]}...")
            
            # Build cast command for InputBox
            cast_cmd = [
                "cast", "send", self.input_box_address,
                "addInput(address,bytes)",
                self.dapp_address,
                f"0x{command_hex}",
                "--rpc-url", self.rpc_url,
                "--private-key", self.private_key,
                "--gas-limit", "200000"
            ]
            
            # Execute cast command
            result = subprocess.run(
                cast_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Extract transaction hash from output
                output_lines = result.stdout.strip().split('\n')
                tx_hash = None
                for line in output_lines:
                    if 'transactionHash' in line:
                        tx_hash = line.split()[-1]
                        break
                
                logger.info(f"✅ Successfully sent registration for {command['device_id']}")
                if tx_hash:
                    logger.info(f"📋 Transaction hash: {tx_hash}")
                return True
            else:
                logger.error(f"❌ Cast command failed for {command['device_id']}")
                logger.error(f"Error: {result.stderr}")
                logger.error(f"Output: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Cast command timed out for {command['device_id']}")
            return False
        except Exception as e:
            logger.error(f"❌ Exception sending cast command for {command['device_id']}: {e}")
            return False
    
    def load_device_mappings(self, csv_path: str = "data/wallet_device_mapping.csv"):
        """Load device to wallet mappings from CSV"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"📋 Loaded {len(df)} device mappings from {csv_path}")
            return df
        except FileNotFoundError:
            logger.error(f"❌ Device mapping file not found: {csv_path}")
            return None
    
    def register_single_device(self, device_id: str, wallet_address: str) -> bool:
        """Register a single device"""
        command = self.create_registration_command(device_id, wallet_address)
        return self.send_cast_command(command)
    
    def register_all_devices(self, csv_path: str = "data/wallet_device_mapping.csv", batch_delay: float = 2.0):
        """Register all devices from CSV mapping"""
        df = self.load_device_mappings(csv_path)
        if df is None:
            return False
        
        success_count = 0
        total_count = len(df)
        
        logger.info(f"🔑 Starting device registration for {total_count} devices via cast...")
        logger.info(f"⏱️ Using {batch_delay}s delay between transactions")
        
        for i, row in df.iterrows():
            device_id = row['device_id']
            wallet_address = row['wallet_address']
            
            logger.info(f"📦 [{i+1}/{total_count}] Processing: {device_id}")
            
            if self.register_single_device(device_id, wallet_address):
                success_count += 1
            else:
                logger.error(f"❌ Failed to register device: {device_id}")
            
            # Add delay between transactions to avoid rate limiting
            if i < total_count - 1:  # Don't delay after the last transaction
                logger.debug(f"⏳ Waiting {batch_delay}s before next transaction...")
                time.sleep(batch_delay)
        
        logger.info(f"🎉 Registration complete: {success_count}/{total_count} successful")
        
        if success_count == total_count:
            logger.info("✅ All devices registered successfully!")
            logger.info("💡 Wait a few minutes for the lcore-node to process the registrations,")
            logger.info("   then try sending encrypted payloads again.")
        else:
            logger.warning(f"⚠️ {total_count - success_count} devices failed to register")
        
        return success_count > 0
    
    def test_cast_connectivity(self):
        """Test cast and blockchain connectivity"""
        try:
            logger.info("🔍 Testing cast connectivity...")
            
            # Test cast is available
            result = subprocess.run(["cast", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Cast command not found or not working")
                return False
            
            logger.info(f"✅ Cast version: {result.stdout.strip()}")
            
            # Test RPC connectivity
            result = subprocess.run([
                "cast", "block", "latest", 
                "--rpc-url", self.rpc_url
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info("✅ RPC connection successful")
                return True
            else:
                logger.error(f"❌ RPC connection failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Connectivity test failed: {e}")
            return False


def main():
    """Main function for device registration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Register L{CORE} devices via cast commands")
    parser.add_argument(
        "--input-box", 
        default="0xC1f612D9ad2270e31BF41fAdBb92f79B63649133",
        help="Cartesi InputBox contract address"
    )
    parser.add_argument(
        "--dapp", 
        default="0xB7B462b81A10A24e1976C9029Ef8FfBdCFc1a96a",
        help="Cartesi DApp address"
    )
    parser.add_argument(
        "--rpc-url", 
        default="https://rpc.devnet.alchemy.com/7eade438-d743-4dc5-ac64-3480de391200",
        help="RPC endpoint URL"
    )
    parser.add_argument(
        "--private-key", 
        default="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
        help="Private key for transactions"
    )
    parser.add_argument(
        "--csv-path", 
        default="data/wallet_device_mapping.csv", 
        help="Device mapping CSV file"
    )
    parser.add_argument(
        "--delay", 
        type=float,
        default=2.0,
        help="Delay between transactions (seconds)"
    )
    parser.add_argument(
        "--test-connection", 
        action="store_true", 
        help="Test cast and RPC connection only"
    )
    parser.add_argument(
        "--single-device",
        help="Register only a specific device ID"
    )
    
    args = parser.parse_args()
    
    # Initialize registrator
    registrator = CastDeviceRegistrator(
        input_box_address=args.input_box,
        dapp_address=args.dapp,
        rpc_url=args.rpc_url,
        private_key=args.private_key
    )
    
    if args.test_connection:
        # Test connection only
        if registrator.test_cast_connectivity():
            logger.info("🎯 Connection test successful!")
            return 0
        else:
            logger.error("❌ Connection test failed!")
            return 1
    
    # Test connection first
    if not registrator.test_cast_connectivity():
        logger.error("❌ Cannot connect to blockchain")
        return 1
    
    if args.single_device:
        # Register single device
        df = registrator.load_device_mappings(args.csv_path)
        if df is None:
            return 1
        
        device_row = df[df['device_id'] == args.single_device]
        if device_row.empty:
            logger.error(f"❌ Device {args.single_device} not found in CSV")
            return 1
        
        wallet_address = device_row.iloc[0]['wallet_address']
        if registrator.register_single_device(args.single_device, wallet_address):
            logger.info(f"✅ Successfully registered {args.single_device}")
            return 0
        else:
            logger.error(f"❌ Failed to register {args.single_device}")
            return 1
    else:
        # Register all devices
        if registrator.register_all_devices(args.csv_path, args.delay):
            logger.info("🎉 Device registration completed!")
            logger.info("⏱️ Wait 2-3 minutes for lcore-node to process all registrations")
            logger.info("💡 Then try encrypted payloads again - JWS verification should work!")
            return 0
        else:
            logger.error("❌ Device registration failed")
            return 1


if __name__ == "__main__":
    exit(main())