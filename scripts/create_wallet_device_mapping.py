#!/usr/bin/env python3
"""
Wallet-Device Mapping Generator for City Chain IoT System

This script creates 100 wallets and distributes the actual 67 device IDs
across as many wallets as possible to maximize wallet participation.

Distribution Strategy:
- 67 wallets get 1 device each (maximizing participation)
- 33 wallets remain empty
- Total: 67 devices across 67 wallets (67% wallet participation)
"""

import csv
import random
from eth_account import Account
from typing import List, Dict, Tuple
import secrets

# Enable unaudited HD wallet features
Account.enable_unaudited_hdwallet_features()

class WalletDeviceMapper:
    def __init__(self):
        self.actual_device_ids = self._get_actual_device_ids()
        self.wallets = []
        self.device_assignments = {}
        
    def _get_actual_device_ids(self) -> Dict[str, List[str]]:
        """Return the actual device IDs from the transformed datasets"""
        return {
            'agricultural': [
                'did:lcore:agri-R1',
                'did:lcore:agri-R2', 
                'did:lcore:agri-R3'
            ],
            'environmental': [
                'did:lcore:env-101-air',
                'did:lcore:env-101-water',
                'did:lcore:env-102-air',
                'did:lcore:env-102-water',
                'did:lcore:env-103-air',
                'did:lcore:env-103-water',
                'did:lcore:env-104-air',
                'did:lcore:env-104-water',
                'did:lcore:env-105-air',
                'did:lcore:env-105-water'
            ],
            'health': [
                'did:lcore:health-tracker-1',
                'did:lcore:health-tracker-2',
                'did:lcore:health-tracker-3',
                'did:lcore:health-tracker-4',
                'did:lcore:health-tracker-5',
                'did:lcore:health-tracker-6',
                'did:lcore:health-tracker-7',
                'did:lcore:health-tracker-8',
                'did:lcore:health-tracker-9',
                'did:lcore:health-tracker-10'
            ],
            'network': [
                'did:lcore:cell-tower-tower-1',
                'did:lcore:cell-tower-tower-2',
                'did:lcore:cell-tower-tower-3',
                'did:lcore:cell-tower-tower-4',
                'did:lcore:cell-tower-tower-5',
                'did:lcore:cell-tower-tower-6',
                'did:lcore:cell-tower-tower-7',
                'did:lcore:cell-tower-tower-8',
                'did:lcore:cell-tower-tower-9'
            ],
            'retail': [
                'did:lcore:retail-39th-street-district-store-1',
                'did:lcore:retail-39th-street-district-store-2',
                'did:lcore:retail-39th-street-district-store-3',
                'did:lcore:retail-brookside-store-1',
                'did:lcore:retail-brookside-store-2',
                'did:lcore:retail-brookside-store-3',
                'did:lcore:retail-country-club-plaza-store-1',
                'did:lcore:retail-country-club-plaza-store-2',
                'did:lcore:retail-country-club-plaza-store-3',
                'did:lcore:retail-crossroads-arts-district-store-1',
                'did:lcore:retail-crossroads-arts-district-store-2',
                'did:lcore:retail-crossroads-arts-district-store-3',
                'did:lcore:retail-crown-center-store-1',
                'did:lcore:retail-crown-center-store-2',
                'did:lcore:retail-crown-center-store-3',
                'did:lcore:retail-midtown-store-1',
                'did:lcore:retail-midtown-store-2',
                'did:lcore:retail-midtown-store-3',
                'did:lcore:retail-power-and-light-district-store-1',
                'did:lcore:retail-power-and-light-district-store-2',
                'did:lcore:retail-power-and-light-district-store-3',
                'did:lcore:retail-river-market-store-1',
                'did:lcore:retail-river-market-store-2',
                'did:lcore:retail-river-market-store-3',
                'did:lcore:retail-west-bottoms-store-1',
                'did:lcore:retail-west-bottoms-store-2',
                'did:lcore:retail-west-bottoms-store-3',
                'did:lcore:retail-westport-store-1',
                'did:lcore:retail-westport-store-2',
                'did:lcore:retail-westport-store-3'
            ],
            'weather': [
                'did:lcore:weather-station-oakland-1',
                'did:lcore:weather-station-oakland-2',
                'did:lcore:weather-station-oakland-3',
                'did:lcore:weather-station-oakland-4',
                'did:lcore:weather-station-oakland-5'
            ]
        }
    
    def generate_wallets(self, count: int = 100) -> List[Dict[str, str]]:
        """Generate specified number of wallets with private keys and addresses"""
        print(f"🔑 Generating {count} Ethereum wallets...")
        
        wallets = []
        for i in range(count):
            # Generate a random private key
            private_key = "0x" + secrets.token_hex(32)
            account = Account.from_key(private_key)
            
            wallet = {
                'wallet_id': f"wallet_{i+1:03d}",
                'address': account.address,
                'private_key': private_key
            }
            wallets.append(wallet)
            
        print(f"✅ Generated {len(wallets)} wallets successfully")
        return wallets
    
    def distribute_devices_across_all_wallets(self) -> Dict[str, List[str]]:
        """
        Distribute devices to maximize wallet participation
        Strategy: Each device gets its own wallet (1 device per wallet)
        Result: 67 wallets with devices, 33 empty wallets
        """
        print("📱 Distributing devices to maximize wallet participation...")
        
        # Flatten all device IDs
        all_devices = []
        for category, devices in self.actual_device_ids.items():
            all_devices.extend(devices)
        
        # Shuffle devices for random distribution
        random.shuffle(all_devices)
        
        print(f"📊 Total devices to distribute: {len(all_devices)}")
        
        assignments = {}
        
        # Assign one device per wallet for maximum participation
        for i, device_id in enumerate(all_devices):
            wallet_id = f"wallet_{i + 1:03d}"
            assignments[wallet_id] = [device_id]
        
        # Calculate distribution stats
        wallets_with_devices = len(assignments)
        empty_wallets = 100 - wallets_with_devices
        participation_rate = (wallets_with_devices / 100) * 100
        
        print(f"✅ Distribution completed:")
        print(f"   📈 Wallets with devices: {wallets_with_devices}")
        print(f"   📭 Empty wallets: {empty_wallets}")
        print(f"   🎯 Participation rate: {participation_rate:.0f}%")
        print(f"   📱 Device distribution: {wallets_with_devices} wallets with 1 device each")
        
        return assignments
    
    def create_mapping_csv(self, output_file: str = "wallet_device_mapping.csv") -> None:
        """Create comprehensive CSV file with wallet-device mappings"""
        print(f"📝 Creating mapping CSV file: {output_file}")
        
        # Generate wallets and distribute devices
        self.wallets = self.generate_wallets(100)
        device_assignments = self.distribute_devices_across_all_wallets()
        
        # Calculate statistics
        total_devices = sum(len(devices) for devices in self.actual_device_ids.values())
        assigned_devices = sum(len(devices) for devices in device_assignments.values())
        wallets_with_devices = len(device_assignments)
        empty_wallets = 100 - wallets_with_devices
        
        # Create detailed mapping
        detailed_mappings = []
        
        for wallet in self.wallets:
            wallet_id = wallet['wallet_id']
            wallet_devices = device_assignments.get(wallet_id, [])
            
            if wallet_devices:
                # Create one row per device (should be just 1 device per wallet)
                for device_id in wallet_devices:
                    # Determine device category
                    category = "unknown"
                    for cat, devices in self.actual_device_ids.items():
                        if device_id in devices:
                            category = cat
                            break
                    
                    detailed_mappings.append({
                        'wallet_id': wallet_id,
                        'wallet_address': wallet['address'],
                        'private_key': wallet['private_key'],
                        'device_id': device_id,
                        'device_category': category,
                        'devices_owned': len(wallet_devices)
                    })
            else:
                # Empty wallet
                detailed_mappings.append({
                    'wallet_id': wallet_id,
                    'wallet_address': wallet['address'],
                    'private_key': wallet['private_key'],
                    'device_id': '',
                    'device_category': '',
                    'devices_owned': 0
                })
        
        # Write to CSV
        fieldnames = ['wallet_id', 'wallet_address', 'private_key', 'device_id', 'device_category', 'devices_owned']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(detailed_mappings)
        
        # Create summary CSV
        summary_file = output_file.replace('.csv', '_summary.csv')
        self._create_summary_csv(summary_file, device_assignments)
        
        # Print final statistics
        print(f"\n📊 Final Statistics:")
        print(f"   Total wallets created: 100")
        print(f"   Wallets with devices: {wallets_with_devices} ({(wallets_with_devices/100)*100:.0f}%)")
        print(f"   Empty wallets: {empty_wallets} ({(empty_wallets/100)*100:.0f}%)")
        print(f"   Total unique devices: {total_devices}")
        print(f"   Devices assigned: {assigned_devices}")
        print(f"   Device assignment rate: {(assigned_devices/total_devices)*100:.1f}%")
        
        # Category breakdown
        print(f"\n📋 Device Category Distribution:")
        for category, devices in self.actual_device_ids.items():
            print(f"   {category.capitalize()}: {len(devices)} devices")
        
        print(f"\n✅ Files created:")
        print(f"   📋 {output_file} - Detailed wallet-device mappings")
        print(f"   📈 {summary_file} - Wallet ownership summary")
    
    def _create_summary_csv(self, summary_file: str, device_assignments: Dict[str, List[str]]) -> None:
        """Create a summary CSV showing wallet ownership patterns"""
        summary_data = []
        
        for wallet in self.wallets:
            wallet_id = wallet['wallet_id']
            devices = device_assignments.get(wallet_id, [])
            
            # Count devices by category
            category_counts = {cat: 0 for cat in self.actual_device_ids.keys()}
            for device_id in devices:
                for cat, cat_devices in self.actual_device_ids.items():
                    if device_id in cat_devices:
                        category_counts[cat] += 1
                        break
            
            summary_data.append({
                'wallet_id': wallet_id,
                'wallet_address': wallet['address'],
                'total_devices': len(devices),
                'agricultural_devices': category_counts['agricultural'],
                'environmental_devices': category_counts['environmental'], 
                'health_devices': category_counts['health'],
                'network_devices': category_counts['network'],
                'retail_devices': category_counts['retail'],
                'weather_devices': category_counts['weather'],
                'device_list': '; '.join(devices) if devices else 'None'
            })
        
        summary_fieldnames = [
            'wallet_id', 'wallet_address', 'total_devices',
            'agricultural_devices', 'environmental_devices', 'health_devices',
            'network_devices', 'retail_devices', 'weather_devices', 'device_list'
        ]
        
        with open(summary_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=summary_fieldnames)
            writer.writeheader()
            writer.writerows(summary_data)

def main():
    """Main execution function"""
    print("🚀 City Chain IoT Wallet-Device Mapping Generator")
    print("📈 Maximum Wallet Participation Strategy")
    print("=" * 60)
    
    # Set random seed for reproducible results
    random.seed(42)
    
    # Create mapper and generate files
    mapper = WalletDeviceMapper()
    mapper.create_mapping_csv("wallet_device_mapping.csv")
    
    print("\n🎉 Wallet-device mapping generation completed!")
    print("\n📈 Optimized for maximum wallet participation:")
    print("   • 67 wallets with 1 device each (67% participation)")
    print("   • 33 empty wallets (available for expansion)")
    print("   • Perfect 1:1 device-to-wallet ratio where possible")
    
    print("\nNext steps:")
    print("1. Review wallet_device_mapping.csv for detailed mappings")
    print("2. Check wallet_device_mapping_summary.csv for ownership overview")
    print("3. Use these wallets in your City Chain IoT simulation")

if __name__ == "__main__":
    main() 