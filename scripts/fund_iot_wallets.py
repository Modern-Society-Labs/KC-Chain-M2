#!/usr/bin/env python3
"""
Mass ETH Distribution Script for IoT Device Wallets

This script distributes ETH from a funded source wallet to all 67 IoT device wallets
to enable them to pay gas fees for blockchain transactions.

Usage:
    python3 scripts/fund_iot_wallets.py --source-key 0x1234... --amount-per-wallet 0.008

Requirements:
    - Source wallet must have enough ETH to fund all devices
    - cast (Foundry) must be installed
    - wallet_device_mapping.csv must exist
"""

import csv
import sys
import argparse
import subprocess
import asyncio
from decimal import Decimal
from typing import List, Dict

# Network configuration
RPC_URL = "https://rpc.devnet.alchemy.com/7eade438-d743-4dc5-ac64-3480de391200"
GAS_LIMIT = "1000000"  # Higher gas limit for devnet compatibility

class WalletFunder:
    def __init__(self, source_private_key: str, rpc_url: str = RPC_URL):
        self.source_private_key = source_private_key
        self.rpc_url = rpc_url
        self.device_wallets = []
        
    def load_device_wallets(self, csv_file: str = "wallet_device_mapping.csv") -> List[Dict[str, str]]:
        """Load device wallet addresses from CSV"""
        wallets = []
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['device_id']:  # Only wallets with devices
                        wallets.append({
                            'address': row['wallet_address'],
                            'device_id': row['device_id'],
                            'wallet_id': row['wallet_id']
                        })
            
            print(f"✅ Loaded {len(wallets)} device wallets from {csv_file}")
            return wallets
            
        except FileNotFoundError:
            print(f"❌ Error: {csv_file} not found. Run create_wallet_device_mapping.py first.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading wallets: {e}")
            sys.exit(1)
    
    def get_source_balance(self) -> Decimal:
        """Get source wallet ETH balance"""
        try:
            result = subprocess.run([
                "cast", "balance", self.get_source_address(),
                "--rpc-url", self.rpc_url
            ], capture_output=True, text=True, check=True)
            
            # Convert wei to ETH
            wei_balance = int(result.stdout.strip())
            eth_balance = Decimal(wei_balance) / Decimal(10**18)
            return eth_balance
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error getting source balance: {e.stderr}")
            sys.exit(1)
    
    def get_source_address(self) -> str:
        """Get source wallet address from private key"""
        try:
            result = subprocess.run([
                "cast", "wallet", "address", self.source_private_key
            ], capture_output=True, text=True, check=True)
            
            return result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error getting source address: {e.stderr}")
            sys.exit(1)
    
    def estimate_gas_cost(self, num_transactions: int) -> Decimal:
        """Estimate total gas cost for all transfers"""
        try:
            # Get current gas price
            result = subprocess.run([
                "cast", "gas-price", "--rpc-url", self.rpc_url
            ], capture_output=True, text=True, check=True)
            
            gas_price_wei = int(result.stdout.strip())
            gas_cost_per_tx = Decimal(gas_price_wei * int(GAS_LIMIT)) / Decimal(10**18)
            total_gas_cost = gas_cost_per_tx * num_transactions
            
            print(f"📊 Gas price: {gas_price_wei} wei")
            print(f"📊 Gas cost per transfer: {gas_cost_per_tx:.6f} ETH")
            print(f"📊 Total gas cost: {total_gas_cost:.6f} ETH")
            
            return total_gas_cost
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not get gas price: {e.stderr}")
            # Fallback estimate
            fallback_cost = Decimal("0.0001") * num_transactions
            print(f"📊 Using fallback gas estimate: {fallback_cost:.6f} ETH")
            return fallback_cost
    
    def transfer_eth(self, to_address: str, amount: str, device_id: str) -> bool:
        """Transfer ETH to a single address"""
        try:
            result = subprocess.run([
                "cast", "send", to_address,
                "--value", amount,
                "--private-key", self.source_private_key,
                "--rpc-url", self.rpc_url,
                "--gas-limit", GAS_LIMIT
            ], capture_output=True, text=True, check=True)
            
            tx_hash = result.stdout.strip()
            print(f"✅ {device_id}: {amount} ETH → {to_address[:8]}... | TX: {tx_hash[:10]}...")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {device_id}: Failed to transfer to {to_address[:8]}... | Error: {e.stderr.strip()}")
            return False
    
    async def fund_all_wallets(self, amount_per_wallet: Decimal) -> Dict[str, int]:
        """Fund all device wallets with specified amount"""
        self.device_wallets = self.load_device_wallets()
        
        if not self.device_wallets:
            print("❌ No device wallets found!")
            return {"success": 0, "failed": 0}
        
        # Convert ETH to wei string for cast
        wei_amount = str(int(amount_per_wallet * Decimal(10**18)))
        
        print(f"\n🚀 Starting distribution of {amount_per_wallet} ETH to {len(self.device_wallets)} wallets...")
        print(f"💰 Total ETH to distribute: {amount_per_wallet * len(self.device_wallets)} ETH")
        print(f"🔗 Using RPC: {self.rpc_url}")
        print("-" * 80)
        
        success_count = 0
        failed_count = 0
        
        for i, wallet in enumerate(self.device_wallets, 1):
            print(f"[{i:2d}/{len(self.device_wallets)}] ", end="")
            
            if self.transfer_eth(wallet['address'], wei_amount, wallet['device_id']):
                success_count += 1
            else:
                failed_count += 1
            
            # Small delay to avoid overwhelming the RPC
            await asyncio.sleep(0.1)
        
        print("-" * 80)
        print(f"📊 Distribution Summary:")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   💰 Total distributed: {Decimal(success_count) * amount_per_wallet} ETH")
        
        return {"success": success_count, "failed": failed_count}

def main():
    parser = argparse.ArgumentParser(description="Mass distribute ETH to IoT device wallets")
    parser.add_argument("--source-key", required=True, help="Private key of source wallet (0x...)")
    parser.add_argument("--amount-per-wallet", type=float, default=0.008, help="ETH amount per wallet (default: 0.008)")
    parser.add_argument("--csv-file", default="wallet_device_mapping.csv", help="Path to wallet mapping CSV")
    parser.add_argument("--rpc-url", default=RPC_URL, help="RPC URL to use")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    
    args = parser.parse_args()
    
    # Validate private key format
    if not args.source_key.startswith("0x") or len(args.source_key) != 66:
        print("❌ Error: Invalid private key format. Should be 0x followed by 64 hex characters.")
        sys.exit(1)
    
    amount_per_wallet = Decimal(str(args.amount_per_wallet))
    
    print("💰 IoT Wallet Mass Distribution Tool")
    print("=" * 50)
    
    funder = WalletFunder(args.source_key, args.rpc_url)
    
    # Load wallets first to get count
    device_wallets = funder.load_device_wallets(args.csv_file)
    num_wallets = len(device_wallets)
    
    # Get source wallet info
    source_address = funder.get_source_address()
    source_balance = funder.get_source_balance()
    
    # Calculate costs
    total_distribution = amount_per_wallet * num_wallets
    gas_cost = funder.estimate_gas_cost(num_wallets)
    total_needed = total_distribution + gas_cost
    
    print(f"\n📋 Distribution Plan:")
    print(f"   Source wallet: {source_address}")
    print(f"   Source balance: {source_balance:.6f} ETH")
    print(f"   Wallets to fund: {num_wallets}")
    print(f"   Amount per wallet: {amount_per_wallet} ETH")
    print(f"   Total distribution: {total_distribution:.6f} ETH")
    print(f"   Estimated gas cost: {gas_cost:.6f} ETH")
    print(f"   Total needed: {total_needed:.6f} ETH")
    
    # Check if source has enough balance
    if source_balance < total_needed:
        print(f"\n❌ Insufficient funds!")
        print(f"   Need: {total_needed:.6f} ETH")
        print(f"   Have: {source_balance:.6f} ETH")
        print(f"   Short: {total_needed - source_balance:.6f} ETH")
        sys.exit(1)
    
    if args.dry_run:
        print(f"\n🔍 DRY RUN: Would distribute {amount_per_wallet} ETH to {num_wallets} wallets")
        print("   Add --no-dry-run to execute actual transfers")
        return
    
    # Confirmation
    print(f"\n⚠️  Ready to distribute {total_distribution:.6f} ETH to {num_wallets} IoT wallets!")
    response = input("Continue? (yes/no): ").lower().strip()
    
    if response != "yes":
        print("❌ Cancelled by user")
        sys.exit(0)
    
    # Execute distribution
    print(f"\n🚀 Starting distribution...")
    result = asyncio.run(funder.fund_all_wallets(amount_per_wallet))
    
    if result["success"] == num_wallets:
        print(f"\n🎉 SUCCESS! All {num_wallets} wallets funded!")
        print(f"💡 IoT devices can now make blockchain transactions!")
    else:
        print(f"\n⚠️  Partial success: {result['success']}/{num_wallets} wallets funded")
        if result["failed"] > 0:
            print(f"💡 Retry failed transactions or check RPC connection")

if __name__ == "__main__":
    main() 