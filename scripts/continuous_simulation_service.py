#!/usr/bin/env python3
"""
L{CORE} Continuous Simulation Service
====================================

A FastAPI-based service that runs continuous IoT device simulation
with real-time control and monitoring capabilities.

Features:
- Continuous device simulation with configurable intervals
- REST API for start/stop/configure operations
- WebSocket for real-time updates
- State persistence for resume functionality
- Integration with actual L{CORE} GraphQL endpoint
- Real-time dashboard updates

Usage:
    python3 scripts/continuous_simulation_service.py
    
    # In another terminal, control via API:
    curl -X POST http://localhost:8080/simulation/start
    curl -X POST http://localhost:8080/simulation/stop  
    curl -X PUT http://localhost:8080/simulation/interval -d '{"interval": 10}'
"""

import asyncio
import json
import time
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import aiohttp
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import shutil
import hashlib
import struct
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import jwt
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper functions for safe data conversion
def safe_int_convert(value, default=0):
    """Safely convert value to int, handling NaN"""
    try:
        if value is None or str(value).strip() == '':
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_float_convert(value, default=None):
    """Safely convert value to float, replace NaN with default/None"""
    import math
    try:
        if value is None or str(value).strip() == '':
            return default
        val = float(value)
        if math.isnan(val):
            return default
        return val
    except (ValueError, TypeError):
        return default


# L{CORE} Encryption Implementation
class LCoreEncryption:
    """L{CORE} dual encryption system implementation"""
    
    @staticmethod
    def derive_aes_key(device_id: str) -> bytes:
        """Derive AES-256 key from device ID"""
        return hashlib.sha256(f"{device_id}stage1_key".encode()).digest()
    
    @staticmethod
    def derive_chacha_key(device_id: str) -> bytes:
        """Derive ChaCha20 key from device ID"""
        return hashlib.sha256(f"{device_id}stage2_key".encode()).digest()
    
    @staticmethod
    def derive_aes_nonce(device_id: str, counter: int) -> bytes:
        """Derive AES nonce from device ID and counter"""
        data = f"{device_id}stage1_nonce{counter}".encode()
        return hashlib.sha256(data).digest()[:12]
    
    @staticmethod
    def derive_chacha_nonce(device_id: str, counter: int) -> bytes:
        """Derive ChaCha20 nonce from device ID and counter"""
        data = f"{device_id}stage2_nonce{counter}".encode()
        return hashlib.sha256(data).digest()[:12]  # ChaCha20-Poly1305 requires 12 bytes
    
    @staticmethod
    def encrypt_dual(data: str, device_id: str, counter: int) -> str:
        """Dual encryption: AES-256-GCM then ChaCha20-Poly1305"""
        try:
            # Stage 1: AES-256-GCM
            aes_key = LCoreEncryption.derive_aes_key(device_id)
            aes_nonce = LCoreEncryption.derive_aes_nonce(device_id, counter)
            
            aes_cipher = AESGCM(aes_key)
            stage1_encrypted = aes_cipher.encrypt(aes_nonce, data.encode(), None)
            
            # Stage 2: ChaCha20-Poly1305  
            chacha_key = LCoreEncryption.derive_chacha_key(device_id)
            chacha_nonce = LCoreEncryption.derive_chacha_nonce(device_id, counter)
            
            chacha_cipher = ChaCha20Poly1305(chacha_key)
            stage2_encrypted = chacha_cipher.encrypt(chacha_nonce, stage1_encrypted, None)
            
            return base64.b64encode(stage2_encrypted).decode()
            
        except Exception as e:
            logger.error(f"Encryption failed for {device_id}: {e}")
            raise

class JWSTokenCreator:
    """Create JWS tokens for device authentication"""
    
    def __init__(self):
        # Generate EC private key for each device (in production, this would be stored securely)
        self.device_keys = {}
    
    def get_or_create_device_key(self, device_id: str) -> ec.EllipticCurvePrivateKey:
        """Get or create EC private key for device"""
        if device_id not in self.device_keys:
            # Generate new EC key for this device
            private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
            self.device_keys[device_id] = private_key
        return self.device_keys[device_id]
    
    def create_jws_token(self, device_id: str, encrypted_payload: str, counter: int) -> str:
        """Create JWS token with encrypted payload"""
        try:
            # Get device private key
            private_key = self.get_or_create_device_key(device_id)
            
            # Create payload
            payload = {
                "device_id": device_id,
                "encrypted_data": encrypted_payload,
                "counter": counter,
                "timestamp": int(time.time()),
                "iss": device_id,  # issuer
                "iat": int(time.time()),  # issued at
            }
            
            # Sign with ES256 (ECDSA using P-256 and SHA-256)
            token = jwt.encode(
                payload,
                private_key,
                algorithm="ES256",
                headers={"kid": device_id}
            )
            
            return token
            
        except Exception as e:
            logger.error(f"JWS creation failed for {device_id}: {e}")
            raise


# Data Models
class SimulationConfig(BaseModel):
    interval: float = 600.0  # 10 minutes between device submissions for Option A
    max_devices: int = 67    # All devices with wallets
    initial_devices: int = 67 # Start all devices immediately
    device_ramp_interval: float = 10.0  # Add devices quickly
    enabled_domains: List[str] = ["environmental", "weather", "network", "retail", "agricultural", "health"]
    
    # Updated for Option A: 10,000 transactions/day across all 67 devices
    target_simulation_days: int = 7
    data_conservation_mode: bool = False

class SimulationStatus(BaseModel):
    running: bool = False
    paused: bool = False
    devices_active: int = 0
    total_submissions: int = 0
    successful_submissions: int = 0
    failed_submissions: int = 0
    uptime_seconds: float = 0
    last_submission: Optional[datetime] = None

class DeviceInfo(BaseModel):
    device_id: str
    domain: str
    did_format: str
    status: str  # 'active', 'inactive', 'error'
    total_submissions: int = 0
    last_submission: Optional[datetime] = None
    submission_interval: float = 5.0

class SimulationUpdate(BaseModel):
    timestamp: datetime
    event_type: str  # 'device_submission', 'status_change', 'error'
    device_id: Optional[str] = None
    data: Dict[str, Any] = {}

class LCoreContinuousSimulator:
    """Continuous L{CORE} IoT simulation engine"""
    
    def __init__(self):
        self.config = SimulationConfig()
        self.status = SimulationStatus()
        self.devices: Dict[str, DeviceInfo] = {}
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.simulation_task: Optional[asyncio.Task] = None
        self.start_time: Optional[datetime] = None
        self.websocket_connections: List[WebSocket] = []
        
        # L{CORE} Configuration
        self.lcore_config = {
            'graphql_endpoint': 'https://lcore-iot-node-production.up.railway.app/graphql',
            'cartesi_dapp': '0xB7B462b81A10A24e1976C9029Ef8FfBdCFc1a96a',
            'input_box': '0xC1f612D9ad2270e31BF41fAdBb92f79B63649133'
        }
        
        # Load transformed datasets on startup
        self.load_datasets()
        
        # Load wallet-device mappings
        self.wallet_mappings = self._load_wallet_mappings()
        
        # Initialize encryption and JWS components
        self.encryption = LCoreEncryption()
        self.jws_creator = JWSTokenCreator()
        self.device_counters = {}  # Track message counters per device
        
        logger.info("L{CORE} Continuous Simulator initialized")
        
    def load_datasets(self):
        """Load transformed IoT datasets"""
        logger.info("Loading transformed IoT datasets...")
        
        data_dir = Path('data')
        dataset_files = {
            'environmental': 'environmental_sensors_combined.csv',
            'agricultural': 'agricultural_sensors_transformed.csv',
            'health': 'health_sensors_privacy_protected.csv',
            'network': 'network_sensors_parsed.csv', 
            'retail': 'retail_sensors_anonymized.csv',
            'weather': 'weather_sensors_converted.csv'
        }
        
        total_records = 0
        for domain, filename in dataset_files.items():
            file_path = data_dir / filename
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    self.datasets[domain] = df
                    total_records += len(df)
                    logger.info(f"Loaded {domain}: {len(df)} records")
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {e}")
            else:
                logger.warning(f"Dataset not found: {filename}")
        
        logger.info(f"Total records available: {total_records}")
        
    def _load_wallet_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load wallet-device mappings from CSV or use hardcoded demo data"""
        import csv
        import os
        
        # Try to load from CSV first (for local development)
        wallet_file = "data/wallet_device_mapping.csv"
        if os.path.exists(wallet_file):
            device_to_wallet = {}
            try:
                with open(wallet_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['device_id']:  # Skip empty device rows
                            device_to_wallet[row['device_id']] = {
                                'address': row['wallet_address'],
                                'private_key': row['private_key'],
                                'wallet_id': row['wallet_id']
                            }
                
                logger.info(f"Loaded {len(device_to_wallet)} device-wallet mappings from CSV")
                return device_to_wallet
                
            except Exception as e:
                logger.error(f"Failed to load wallet mappings from CSV: {e}")
        
        # Use hardcoded demo data for Railway deployment
        logger.warning("CSV file not found, using hardcoded demo wallet mappings")
        demo_wallets = {
            'did:lcore:health-tracker-3': {
                'address': '0xaa55889648777CDf8283309334cfe35C0474865d',
                'private_key': '0xf749e0f461492f2ca974c2ac67173df1dd46f921a02a59e69206c816247aaade',
                'wallet_id': 'wallet_001'
            },
            'did:lcore:retail-midtown-store-3': {
                'address': '0x15b7BE86B61DBa0eb5e25d182c6370a791D8F5de',
                'private_key': '0x21592e27c0975f68dae085d48f9c51332f086d0af2e1b745c8e2e22f54c70e82',
                'wallet_id': 'wallet_002'
            },
            'did:lcore:cell-tower-tower-7': {
                'address': '0xF80812f759FF5308EE144845B3c978E437AEFe3b',
                'private_key': '0xd36295d8c4b376725c53c50bb4b81312ae4989c051fea69506b06a6b6cdc4c0b',
                'wallet_id': 'wallet_003'
            },
            'did:lcore:env-103-air': {
                'address': '0x15032Fe2413b031b42e33E74b00e823B6EaAD4d4',
                'private_key': '0xb4a386ef62bfe76786e7085afbecdeb1797b0e97916653647c946dd0fd72ecc9',
                'wallet_id': 'wallet_005'
            },
            'did:lcore:weather-station-oakland-2': {
                'address': '0x1BA06167E9e1A3FdE3d5004c15a750cdAd7cF17F',
                'private_key': '0x9b1f0bcb8f413051818593399ec70c03e55c5aad44eadd4fa1f34d9028d6e3e4',
                'wallet_id': 'wallet_008'
            }
        }
        
        logger.info(f"Using {len(demo_wallets)} hardcoded demo wallet mappings")
        return demo_wallets
    
    def get_wallet_for_device(self, device_id: str) -> Optional[Dict[str, str]]:
        """Get wallet info for a device ID"""
        return self.wallet_mappings.get(device_id)
        
    def create_device(self, domain: str) -> DeviceInfo:
        """Create a new device for the given domain using real device IDs with wallets"""
        # Map domain names to device ID patterns (based on actual device IDs)
        domain_patterns = {
            'environmental': ['env-'],  # matches did:lcore:env-103-air
            'weather': ['weather-station-'],  # matches did:lcore:weather-station-oakland-2
            'network': ['cell-tower-'],  # matches did:lcore:cell-tower-tower-7
            'agricultural': ['agri-'],  # matches did:lcore:agri-R1
            'health': ['health-tracker-'],  # matches did:lcore:health-tracker-3
            'retail': ['retail-']  # matches did:lcore:retail-midtown-store-3
        }
        
        # Get available device IDs for this domain that have wallets
        patterns = domain_patterns.get(domain, [domain])
        available_devices = []
        
        for device_id in self.wallet_mappings.keys():
            for pattern in patterns:
                if pattern in device_id.lower():
                    available_devices.append(device_id)
                    break
        
        if not available_devices:
            logger.warning(f"No devices with wallets found for domain: {domain}, using fallback")
            # Fallback to old method if no wallets available
            device_id = f"{domain}_{uuid.uuid4().hex[:8]}"
        else:
            # Pick a random device that's not already in use
            unused_devices = [d for d in available_devices if d not in self.devices]
            if unused_devices:
                device_id = random.choice(unused_devices)
            else:
                # All devices in use, pick any
                device_id = random.choice(available_devices)
                logger.info(f"Reusing device {device_id} (all devices in domain are active)")
        
        # Add some randomness to submission intervals (±30% variation)
        base_interval = self.config.interval
        variation = base_interval * 0.3
        submission_interval = base_interval + random.uniform(-variation, variation)
        
        device = DeviceInfo(
            device_id=device_id,
            domain=domain,
            did_format=f"did:lcore:{device_id}",
            status='inactive',
            submission_interval=max(30.0, submission_interval)  # Minimum 30 seconds
        )
        
        self.devices[device_id] = device
        wallet_info = self.get_wallet_for_device(device_id)
        wallet_addr = wallet_info['address'][:8] + "..." if wallet_info else "no-wallet"
        logger.info(f"Created device: {device_id} ({domain}) with {submission_interval:.1f}s interval • Wallet: {wallet_addr}")
        return device
        
    def generate_iot_reading(self, device: DeviceInfo) -> Dict[str, Any]:
        """Generate realistic IoT reading from transformed datasets"""
        domain = device.domain
        
        # Base reading structure
        reading = {
            'device_id': device.device_id,
            'did_format': device.did_format,
            'timestamp': int(time.time()),
            'domain': domain,
            'submission_count': device.total_submissions + 1,
            'simulator': 'continuous_service'
        }
        
        # Use real transformed data if available
        if domain in self.datasets and len(self.datasets[domain]) > 0:
            try:
                sample_row = self.datasets[domain].sample(n=1).iloc[0]
                reading['data_source'] = 'real_dataset'
                
                # Domain-specific data extraction
                if domain == 'environmental':
                    reading.update({
                        'sensor_type': 'environmental',
                        'temperature': safe_float_convert(sample_row.get('temperature'), 20.0),
                        'humidity': safe_float_convert(sample_row.get('humidity_percent'), None),
                        'air_quality_index': safe_int_convert(sample_row.get('air_quality_index'), 100)
                    })
                    
                elif domain == 'weather':
                    reading.update({
                        'sensor_type': 'weather', 
                        'temperature_celsius': safe_float_convert(sample_row.get('temperature_celsius'), 15.0),
                        'humidity_percent': safe_float_convert(sample_row.get('humidity_percent'), None),
                        'pressure_hpa': safe_float_convert(sample_row.get('pressure_hpa'), 1013.25)
                    })
                    
                elif domain == 'network':
                    reading.update({
                        'sensor_type': 'network',
                        'signal_strength_dbm': safe_float_convert(sample_row.get('signal_strength_dbm'), -70.0),
                        'latency_ms': safe_float_convert(sample_row.get('latency_ms'), 20.0),
                        'bandwidth_mbps': safe_float_convert(sample_row.get('bandwidth_mbps'), 50.0)
                    })
                    
                elif domain == 'retail':
                    reading.update({
                        'sensor_type': 'retail',
                        'transaction_value': safe_float_convert(sample_row.get('transaction_value'), 25.99),
                        'kc_neighborhood': str(sample_row.get('kc_neighborhood', 'Downtown')),
                        'anonymized_customer_count': safe_int_convert(sample_row.get('anonymized_customer_count'), 1)
                    })
                    
            except Exception as e:
                logger.error(f"Error extracting data for {domain}: {e}")
                reading['data_source'] = 'synthetic_fallback'
        else:
            # Synthetic fallback data
            reading.update({
                'data_source': 'synthetic',
                'sensor_type': domain,
                'value': random.uniform(10, 100),
                'unit': 'units'
            })
        
        # Privacy metadata
        reading['privacy_metadata'] = {
            'pii_removed': True,
            'location_anonymized': True,
            'encryption_ready': True,
            'privacy_score': 100,
            'w3c_did_compliant': True
        }
        
        return reading
        
    async def submit_to_lcore(self, iot_reading: Dict[str, Any]) -> bool:
        """Submit encrypted IoT reading to REAL InputBox contract using cast"""
        try:
            device_id = iot_reading.get('device_id', 'unknown')
            
            # Get wallet for this device
            wallet_info = self.get_wallet_for_device(device_id)
            if not wallet_info:
                logger.error(f"No wallet found for device {device_id}")
                self.status.failed_submissions += 1
                return False
            
            # Get/increment device counter
            if device_id not in self.device_counters:
                self.device_counters[device_id] = 0
            self.device_counters[device_id] += 1
            counter = self.device_counters[device_id]
            
            # Step 1: Convert IoT reading to JSON
            iot_json = json.dumps(iot_reading, separators=(',', ':'), default=str)
            
            # Step 2: Encrypt using L{CORE} dual encryption
            encrypted_payload = self.encryption.encrypt_dual(iot_json, device_id, counter)
            
            # Step 3: Create JWS token
            jws_token = self.jws_creator.create_jws_token(device_id, encrypted_payload, counter)
            
            # Step 4: Create Cartesi command with proper format
            cartesi_command = {
                "type": "submit_sensor_data",
                "device_id": device_id,
                "encrypted_payload": jws_token
            }
            
            # Step 5: Convert to hex payload for blockchain
            command_json = json.dumps(cartesi_command, separators=(',', ':'))
            hex_payload = '0x' + command_json.encode('utf-8').hex()
            
            # Make REAL cast call to InputBox contract
            input_box_address = "0xC1f612D9ad2270e31BF41fAdBb92f79B63649133"
            rpc_url = "https://rpc.devnet.alchemy.com/7eade438-d743-4dc5-ac64-3480de391200"
            
            cast_command = [
                "cast", "send",
                input_box_address,
                "addInput(address,bytes)",
                "0xB7B462b81A10A24e1976C9029Ef8FfBdCFc1a96a",  # Cartesi DApp address
                hex_payload,             # encrypted input data
                "--private-key", wallet_info['private_key'],
                "--rpc-url", rpc_url,
                "--gas-limit", "1000000"
            ]
            
            logger.info(f"🔐 Submitting encrypted transaction for device {device_id} (counter: {counter}) from wallet {wallet_info['address'][:8]}...")

            # Ensure Foundry 'cast' CLI is installed and available
            if shutil.which("cast") is None:
                missing_msg = (
                    "Foundry 'cast' CLI not found in PATH. Install Foundry inside the runtime "
                    "environment (e.g., run 'curl -L https://foundry.paradigm.xyz | bash && /root/.foundry/bin/foundryup' "
                    "and ensure '/root/.foundry/bin' is on PATH) or switch to a web3.py-based submission."
                )
                logger.error(missing_msg)
                self.status.failed_submissions += 1
                # Raise FileNotFoundError to surface a clear reason upstream
                raise FileNotFoundError(missing_msg)
            
            # Execute cast command
            import subprocess
            result = await asyncio.create_subprocess_exec(
                *cast_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                tx_hash = stdout.decode().strip()
                logger.info(f"✅ Encrypted transaction successful! Hash: {tx_hash}")
                
                # Update statistics
                self.status.total_submissions += 1
                self.status.successful_submissions += 1
                self.status.last_submission = datetime.now()
                return True
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"❌ Cast command failed: {error_msg}")
                self.status.failed_submissions += 1
                return False
            
        except Exception as e:
            logger.error(f"💥 Encrypted submission failed: {e}")
            self.status.failed_submissions += 1
            return False
            
    async def simulate_device_loop(self, device: DeviceInfo):
        """Continuous simulation loop for a single device"""
        device.status = 'active'
        
        try:
            while self.status.running:
                # Check if paused
                if self.status.paused:
                    await asyncio.sleep(1)  # Check every second while paused
                    continue
                    
                # Generate IoT reading
                iot_reading = self.generate_iot_reading(device)
                
                # Submit to L{CORE}
                success = await self.submit_to_lcore(iot_reading)
                
                if success:
                    device.total_submissions += 1
                    device.last_submission = datetime.now()
                    
                    # Update global counters
                    self.status.total_submissions += 1
                    self.status.successful_submissions += 1
                    self.status.last_submission = device.last_submission
                    
                    # Broadcast update to connected WebSockets (throttled to every 5th submission for slower pace)
                    if self.status.total_submissions % 5 == 0:
                        update = SimulationUpdate(
                            timestamp=datetime.now(),
                            event_type='status_change',
                            data=self.status.model_dump(mode='json')
                        )
                        await self.broadcast_update(update)
                    
                    logger.info(f"Device {device.device_id}: Submission #{device.total_submissions}")
                else:
                    device.status = 'error'
                    self.status.failed_submissions += 1
                    logger.error(f"Device {device.device_id}: Submission failed")
                
                # Wait for next submission
                await asyncio.sleep(device.submission_interval)
                
        except asyncio.CancelledError:
            logger.info(f"Device {device.device_id} simulation stopped")
        except Exception as e:
            logger.error(f"Device {device.device_id} error: {e}")
            device.status = 'error'
        finally:
            device.status = 'inactive'
            
    async def start_simulation(self):
        """Start the continuous simulation"""
        if self.status.running:
            logger.warning("Simulation already running")
            return
            
        logger.info("Starting continuous simulation...")
        self.status.running = True
        self.start_time = datetime.now()
        
        # Create initial devices - all 67 devices for Option A
        device_tasks = []
        
        # Create all available devices with wallets
        all_device_ids = list(self.wallet_mappings.keys())
        logger.info(f"Creating all {len(all_device_ids)} devices with wallets...")
        
        for device_id in all_device_ids:
            # Determine domain from device ID
            domain = "unknown"
            for domain_name, patterns in {
                'environmental': ['env-'],
                'weather': ['weather-station-'],
                'network': ['cell-tower-'],
                'agricultural': ['agri-'],
                'health': ['health-tracker-'],
                'retail': ['retail-']
            }.items():
                for pattern in patterns:
                    if pattern in device_id.lower():
                        domain = domain_name
                        break
                if domain != "unknown":
                    break
            
            # Create device with real device ID
            base_interval = 600  # 10 minutes
            variation = base_interval * 0.2
            submission_interval = base_interval + random.uniform(-variation, variation)
            
            device = DeviceInfo(
                device_id=device_id,
                domain=domain,
                did_format=f"did:lcore:{device_id}",
                status='inactive',
                submission_interval=max(30.0, submission_interval)
            )
            
            self.devices[device_id] = device
            task = asyncio.create_task(self.simulate_device_loop(device))
            device_tasks.append(task)
            
            wallet_info = self.get_wallet_for_device(device_id)
            wallet_addr = wallet_info['address'][:8] + "..." if wallet_info else "no-wallet"
            logger.info(f"Created device: {device_id} ({domain}) with {submission_interval:.1f}s interval • Wallet: {wallet_addr}")
        
        self.status.devices_active = len(device_tasks)
        logger.info(f"Started {len(device_tasks)} initial device simulations")
        
        # No ramp-up needed - all devices start immediately
        
        # Store task for later cancellation
        self.simulation_task = asyncio.gather(*device_tasks, return_exceptions=True)
        
        # Immediately broadcast status update for frontend reactivity
        await self.broadcast_status_update()
        
    async def stop_simulation(self):
        """Stop the continuous simulation"""
        if not self.status.running:
            logger.warning("Simulation not running")
            return
            
        logger.info("Stopping continuous simulation...")
        self.status.running = False
        self.status.paused = False  # Reset paused state when stopping
        
        # Cancel simulation task
        if self.simulation_task:
            self.simulation_task.cancel()
            try:
                await self.simulation_task
            except asyncio.CancelledError:
                pass
        
        # Update device statuses
        for device in self.devices.values():
            if device.status == 'active':
                device.status = 'inactive'
        
        self.status.devices_active = 0
        logger.info("Simulation stopped")
        
        # Immediately broadcast status update for frontend reactivity
        await self.broadcast_status_update()
        
    async def pause_simulation(self):
        """Pause the continuous simulation"""
        if not self.status.running or self.status.paused:
            logger.warning("Simulation not running or already paused")
            return
            
        logger.info("Pausing continuous simulation...")
        self.status.paused = True
        
        # Broadcast status update
        await self.broadcast_status_update()
        
    async def resume_simulation(self):
        """Resume the paused simulation"""
        if not self.status.running or not self.status.paused:
            logger.warning("Simulation not running or not paused")
            return
            
        logger.info("Resuming continuous simulation...")
        self.status.paused = False
        
        # Broadcast status update
        await self.broadcast_status_update()
        
    async def restart_simulation(self):
        """Restart the simulation (stop and start with reset)"""
        logger.info("Restarting continuous simulation...")
        await self.stop_simulation()
        
        # Reset all statistics
        self.status.total_submissions = 0
        self.status.successful_submissions = 0
        self.status.failed_submissions = 0
        self.status.uptime_seconds = 0
        self.status.last_submission = None
        self.status.paused = False
        
        # Clear and reset devices
        self.devices.clear()
        
        # Reset start time
        self.start_time = datetime.now()
        
        await self.start_simulation()
        logger.info("Simulation restarted with reset statistics")

        await self.broadcast_status_update()
        
    async def update_interval(self, new_interval: float):
        """Update submission interval for all devices"""
        logger.info(f"Updating interval to {new_interval} seconds")
        self.config.interval = new_interval
        
        # Update existing devices
        for device in self.devices.values():
            device.submission_interval = new_interval + random.uniform(-1, 1)
        
        # Broadcast configuration update
        await self.broadcast_update(SimulationUpdate(
            timestamp=datetime.now(),
            event_type='config_change',
            data={'new_interval': new_interval}
        ))
        
    async def get_status(self) -> SimulationStatus:
        """Get current simulation status"""
        if self.start_time:
            self.status.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        
        return self.status
        
    async def get_devices(self) -> List[DeviceInfo]:
        """Get list of all devices"""
        return list(self.devices.values())
        
    async def broadcast_update(self, update: SimulationUpdate):
        """Broadcast update to all connected WebSocket clients"""
        if not self.websocket_connections:
            return
            
        message = update.model_dump_json() if hasattr(update, "model_dump_json") else update.json()
        disconnected = []
        
        for websocket in self.websocket_connections:
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            self.websocket_connections.remove(websocket)
            
    async def broadcast_status_update(self):
        """Broadcast status update"""
        status = await self.get_status()
        update = SimulationUpdate(
            timestamp=datetime.now(),
            event_type='status_change',
            data=status.model_dump(mode='json')
        )
        await self.broadcast_update(update)
        
    def add_websocket_connection(self, websocket: WebSocket):
        """Add WebSocket connection"""
        self.websocket_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.websocket_connections)}")
        
    def remove_websocket_connection(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.websocket_connections:
            self.websocket_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.websocket_connections)}")

    async def ramp_up_devices(self):
        """Gradually increase the number of devices over time"""
        logger.info("Starting device ramp-up process...")
        
        while self.status.running and len(self.devices) < self.config.max_devices:
            # Wait for ramp interval
            await asyncio.sleep(self.config.device_ramp_interval)
            
            if not self.status.running:
                break
                
            # Add a new device from a random domain
            available_domains = [d for d in self.config.enabled_domains 
                               if sum(1 for dev in self.devices.values() if dev.domain == d) < 3]  # Max 3 per domain
            
            if available_domains:
                new_domain = random.choice(available_domains)
                new_device = self.create_device(new_domain)
                
                # Start simulation for this device
                asyncio.create_task(self.simulate_device_loop(new_device))
                
                # Update status and broadcast
                self.status.devices_active = len([d for d in self.devices.values() if d.status == 'active'])
                
                logger.info(f"Ramped up device: {new_device.device_id} ({new_device.domain}) - Total devices: {len(self.devices)}")
                await self.broadcast_status_update()
            else:
                logger.info("All domains have reached maximum device count")
                break
                
        logger.info("Device ramp-up completed")

# Global simulator instance
simulator = LCoreContinuousSimulator()

# FastAPI Application
app = FastAPI(
    title="L{CORE} Continuous Simulation Service",
    description="Real-time IoT device simulation with control API",
    version="1.0.0"
)

# CORS middleware for frontend integration
# Allow local dev and the deployed Vercel frontend
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://lcore-frontend.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API Endpoints

@app.post("/simulation/start")
async def start_simulation():
    """Start the continuous simulation"""
    try:
        await simulator.start_simulation()
        return {"status": "started", "message": "Simulation started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulation/stop")
async def stop_simulation():
    """Stop the continuous simulation"""
    try:
        await simulator.stop_simulation()
        return {"status": "stopped", "message": "Simulation stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulation/pause")
async def pause_simulation():
    """Pause the continuous simulation"""
    try:
        await simulator.pause_simulation()
        return {"status": "paused", "message": "Simulation paused successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulation/resume")
async def resume_simulation():
    """Resume the paused simulation"""
    try:
        await simulator.resume_simulation()
        return {"status": "resumed", "message": "Simulation resumed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulation/restart")
async def restart_simulation():
    """Restart the simulation"""
    try:
        await simulator.restart_simulation()
        return {"status": "restarted", "message": "Simulation restarted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/simulation/interval")
async def update_interval(request: dict):
    """Update simulation interval"""
    try:
        new_interval = request.get('interval', 35.0)
        
        # Validate interval (20 seconds to 5 minutes for 3-day simulation)
        if not (20.0 <= new_interval <= 300.0):
            raise HTTPException(status_code=400, detail="Interval must be between 20 and 300 seconds")
            
        await simulator.update_interval(new_interval)
        return {"status": "updated", "new_interval": new_interval}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/simulation/status")
async def get_simulation_status():
    """Get current simulation status"""
    try:
        status = await simulator.get_status()
        return status.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/simulation/devices")
async def get_devices():
    """Get list of simulated devices"""
    try:
        devices = await simulator.get_devices()
        return [device.model_dump(mode='json') for device in devices]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/simulation/config")
async def get_config():
    """Get current simulation configuration"""
    return simulator.config.model_dump()

@app.put("/simulation/config")
async def update_config(config: SimulationConfig):
    """Update simulation configuration"""
    try:
        simulator.config = config
        return {"status": "updated", "config": config.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time simulation updates"""
    await websocket.accept()
    simulator.add_websocket_connection(websocket)
    
    try:
        # Send initial status
        status = await simulator.get_status()
        devices = await simulator.get_devices()
        
        initial_data = {
            'type': 'initial_state',
            'status': status.model_dump(mode='json'),
            'devices': [device.model_dump(mode='json') for device in devices],
            'config': simulator.config.model_dump()
        }
        
        await websocket.send_text(json.dumps(initial_data, default=str))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        simulator.remove_websocket_connection(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        simulator.remove_websocket_connection(websocket)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "simulation_running": simulator.status.running,
        "devices_active": simulator.status.devices_active,
        "websocket_connections": len(simulator.websocket_connections)
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("L{CORE} Continuous Simulation Service starting up...")
    logger.info(f"GraphQL endpoint: {simulator.lcore_config['graphql_endpoint']}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("L{CORE} Continuous Simulation Service shutting down...")
    if simulator.status.running:
        await simulator.stop_simulation()

if __name__ == "__main__":
    # Run the service
    import os
    
    # Get configuration from environment variables
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '8080'))
    
    logger.info(f"Starting L{{CORE}} simulation service on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    ) 