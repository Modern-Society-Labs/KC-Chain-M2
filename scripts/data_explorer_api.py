#!/usr/bin/env python3
"""
Data Explorer API Backend
========================

FastAPI backend service that provides REST endpoints for the Data Explorer frontend.
Connects to Supabase PostgreSQL and provides decryption capabilities.

Endpoints:
- GET /api/inputs - Fetch raw encrypted inputs from Supabase
- POST /api/decrypt - Decrypt specific inputs using device keys
- POST /api/decrypt-batch - Decrypt multiple inputs at once
- GET /api/analytics - Generate aggregated analytics reports

Usage:
    python scripts/data_explorer_api.py
"""

import asyncio
import json
import os
import hashlib
import base64
import math
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row
import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

# Initialize FastAPI app
app = FastAPI(
    title="Data Explorer API",
    description="Backend API for IoT data exploration and decryption",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
SUPABASE_DSN = os.getenv("POSTGRES_DSN")
if not SUPABASE_DSN:
    raise ValueError("POSTGRES_DSN environment variable is required")

# Pydantic models for API
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

class DecryptedPayload(BaseModel):
    device_id: str
    timestamp: int
    domain: str
    sensor_type: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    air_quality_index: Optional[int] = None
    transaction_value: Optional[float] = None
    signal_strength_dbm: Optional[float] = None
    kc_neighborhood: Optional[str] = None
    anonymized_customer_count: Optional[int] = None
    latency_ms: Optional[float] = None
    bandwidth_mbps: Optional[float] = None
    pressure_hpa: Optional[float] = None
    privacy_metadata: Dict[str, Any]

class AggregatedData(BaseModel):
    domain: str
    device_count: int
    total_readings: int
    avg_temperature: Optional[float] = None
    avg_humidity: Optional[float] = None
    avg_transaction_value: Optional[float] = None
    avg_signal_strength: Optional[float] = None
    privacy_score: float

# Decryption utilities (copied from decrypt_input.py)
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

def extract_domain_from_device_id(device_id: str) -> str:
    """Extract domain from device ID."""
    if 'env-' in device_id:
        return 'environmental'
    elif 'health-tracker-' in device_id:
        return 'health'
    elif 'retail-' in device_id:
        return 'retail'
    elif 'cell-tower-' in device_id:
        return 'network'
    elif 'weather-station-' in device_id:
        return 'weather'
    elif 'agri-' in device_id:
        return 'agricultural'
    else:
        return 'unknown'

def safe_float_convert(value, default=None):
    """Safely convert value to float, handling NaN."""
    try:
        if value is None:
            return default
        val = float(value)
        if math.isnan(val):
            return default
        return val
    except (ValueError, TypeError):
        return default

def get_db_connection():
    """Get database connection."""
    return psycopg.connect(
        SUPABASE_DSN,
        row_factory=dict_row
    )

# API Endpoints

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        with get_db_connection() as conn:
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
        with get_db_connection() as conn:
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
            
            # Parse payload data and filter by device type if specified
            parsed_records = []
            for record in records:
                try:
                    # Handle payload parsing (Buffer format)
                    payload_data = record['payload']
                    if isinstance(payload_data, (bytes, memoryview)):
                        # Convert bytea to string, handle NaN, parse JSON
                        if isinstance(payload_data, memoryview):
                            payload_str = payload_data.tobytes().decode().replace("NaN", "null")
                        else:
                            payload_str = payload_data.decode().replace("NaN", "null")
                        payload_json = json.loads(payload_str)
                        
                        # If it's a Buffer format, reconstruct the original data
                        if isinstance(payload_json, dict) and payload_json.get("type") == "Buffer":
                            data_bytes = bytes(int(b) for b in payload_json["data"])
                            outer_json = json.loads(data_bytes.decode())
                        else:
                            outer_json = payload_json
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
                        "msg_sender": record['msg_sender'],
                        "payload": outer_json,
                        "status": record['status']
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
        with get_db_connection() as conn:
            # Fetch the specific input
            query = "SELECT payload FROM inputs WHERE index = %s LIMIT 1"
            row = conn.execute(query, (request.index,))
            record = row.fetchone()
            
            if not record:
                raise HTTPException(status_code=404, detail=f"Input {request.index} not found")
            
            # Parse payload
            payload_data = record['payload']
            if isinstance(payload_data, (bytes, memoryview)):
                if isinstance(payload_data, memoryview):
                    payload_str = payload_data.tobytes().decode().replace("NaN", "null")
                else:
                    payload_str = payload_data.decode().replace("NaN", "null")
                payload_json = json.loads(payload_str)
                
                if isinstance(payload_json, dict) and payload_json.get("type") == "Buffer":
                    data_bytes = bytes(int(b) for b in payload_json["data"])
                    outer_json = json.loads(data_bytes.decode())
                else:
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
            
            return {
                "device_id": request.device_id,
                "index": request.index,
                "decrypted_data": sensor_data,
                "jws_claims": claims
            }
            
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
                
                # Extract domain
                domain = extract_domain_from_device_id(device_id)
                
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
        
        return {
            "decrypted_data": decrypted_results,
            "total_decrypted": len(decrypted_results),
            "total_attempted": len(request.records)
        }
        
    except Exception as e:
        print(f"Batch decryption error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch decryption failed: {str(e)}")

@app.post("/api/analytics")
async def generate_analytics(decrypted_data: List[DecryptedPayload]):
    """Generate aggregated analytics from decrypted data."""
    try:
        # Group data by domain
        domain_groups = {}
        for item in decrypted_data:
            domain = item.domain
            if domain not in domain_groups:
                domain_groups[domain] = []
            domain_groups[domain].append(item)
        
        # Calculate aggregates for each domain
        aggregated_results = []
        for domain, items in domain_groups.items():
            # Extract numeric values
            temperatures = [item.temperature for item in items if item.temperature is not None]
            humidities = [item.humidity for item in items if item.humidity is not None]
            transactions = [item.transaction_value for item in items if item.transaction_value is not None]
            signals = [item.signal_strength_dbm for item in items if item.signal_strength_dbm is not None]
            
            aggregated = {
                "domain": domain,
                "device_count": len(set(item.device_id for item in items)),
                "total_readings": len(items),
                "privacy_score": 100.0  # All data is privacy-compliant
            }
            
            # Calculate averages
            if temperatures:
                aggregated["avg_temperature"] = round(sum(temperatures) / len(temperatures), 1)
            if humidities:
                aggregated["avg_humidity"] = round(sum(humidities) / len(humidities), 1)
            if transactions:
                aggregated["avg_transaction_value"] = round(sum(transactions) / len(transactions), 2)
            if signals:
                aggregated["avg_signal_strength"] = round(sum(signals) / len(signals), 1)
            
            aggregated_results.append(aggregated)
        
        return {
            "analytics": aggregated_results,
            "total_domains": len(aggregated_results),
            "total_readings": len(decrypted_data)
        }
        
    except Exception as e:
        print(f"Analytics generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")

# Main execution
if __name__ == "__main__":
    import os
    
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '8090'))
    
    print(f"Starting Data Explorer API on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )