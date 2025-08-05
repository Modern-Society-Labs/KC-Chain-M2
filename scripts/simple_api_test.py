#!/usr/bin/env python3
"""Simple test of the API logic"""

import asyncio
import json
import os
import psycopg
from psycopg.rows import dict_row

# Database configuration
SUPABASE_DSN = os.getenv("POSTGRES_DSN")
if not SUPABASE_DSN:
    raise ValueError("POSTGRES_DSN environment variable is required")

async def test_fetch_inputs():
    """Test the fetch inputs logic"""
    try:
        # Use regular psycopg instead of async for testing
        with psycopg.connect(SUPABASE_DSN, row_factory=dict_row) as conn:
            # Build query
            where_clauses = []
            params = []
            
            block_number_min = 108570
            limit = 2
            
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
            
            print(f"Query: {query}")
            print(f"Params: {params}")
            
            rows = conn.execute(query, params)
            records = rows.fetchall()
            
            print(f"Found {len(records)} records")
            
            # Parse payload data
            parsed_records = []
            for record in records:
                try:
                    print(f"Processing record {record['index']}")
                    
                    # Handle payload parsing
                    payload_data = record['payload']
                    if isinstance(payload_data, bytes):
                        payload_str = payload_data.decode().replace("NaN", "null")
                        payload_json = json.loads(payload_str)
                        outer_json = payload_json  # Direct format
                    else:
                        outer_json = payload_data
                    
                    print(f"  Device ID: {outer_json.get('device_id', 'N/A')}")
                    
                    parsed_records.append({
                        "index": record['index'],
                        "block_number": record['block_number'],
                        "timestamp": record['timestamp'].isoformat() if record['timestamp'] else None,
                        "msg_sender": record['msg_sender'].hex() if isinstance(record['msg_sender'], bytes) else record['msg_sender'],
                        "payload": outer_json,
                        "status": str(record['status'])
                    })
                    
                except Exception as e:
                    print(f"Error parsing record {record.get('index', 'unknown')}: {e}")
                    continue
            
            result = {
                "records": parsed_records,
                "total": len(parsed_records),
                "filtered_by": None
            }
            
            print(f"Result: {json.dumps(result, indent=2)}")
            
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    asyncio.run(test_fetch_inputs())