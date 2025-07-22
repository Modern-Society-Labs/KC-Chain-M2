# Wallet-Device Mapping Generator

## Overview
This script creates 100 Ethereum wallets and associates them with the **actual 67 device IDs** from your transformed IoT datasets, optimizing for maximum wallet participation while maintaining realistic ownership patterns.

## Device Distribution Summary
- **Total Devices**: 67 across 6 categories
- **Agricultural**: 3 devices (farm plots)
- **Environmental**: 10 devices (5 air + 5 water sensors)
- **Health**: 10 devices (fitness trackers)
- **Network**: 9 devices (cell towers)
- **Retail**: 30 devices (city chain stores)
- **Weather**: 5 devices (Oakland weather stations)

## Wallet Distribution Strategy
- **45 wallets** with 1 device each (45 devices)
- **8 wallets** with 2 devices each (16 devices)
- **2 wallets** with 3 devices each (6 devices)
- **45 wallets** remain empty (for future expansion)
- **Total**: 67 devices across 55 wallets

## Setup & Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements_wallet_mapping.txt
   ```

2. **Run the script:**
   ```bash
   python create_wallet_device_mapping.py
   ```

## Output Files

### 1. `wallet_device_mapping.csv`
**Detailed mapping with one row per device:**
```csv
wallet_id,wallet_address,private_key,device_id,device_category,devices_owned
wallet_001,0x1234...,0xabcd...,did:lcore:agri-R1,agricultural,1
wallet_002,0x5678...,0xefgh...,did:lcore:env-101-air,environmental,2
wallet_002,0x5678...,0xefgh...,did:lcore:env-101-water,environmental,2
```

### 2. `wallet_device_mapping_summary.csv`
**One row per wallet with category counts:**
```csv
wallet_id,wallet_address,total_devices,agricultural_devices,environmental_devices,health_devices,network_devices,retail_devices,weather_devices,device_list
wallet_001,0x1234...,1,1,0,0,0,0,0,did:lcore:agri-R1
wallet_002,0x5678...,2,0,2,0,0,0,0,did:lcore:env-101-air; did:lcore:env-101-water
```

## Usage in City Chain IoT System

1. **Import wallet data** into your Cartesi application
2. **Use wallet addresses** as `owner_address` in device registrations
3. **Enable paymaster functionality** to cover gas costs
4. **Simulate device data uploads** using the real device IDs
5. **Test economic models** with realistic wallet distribution

## Security Notes

⚠️ **IMPORTANT**: This script generates real private keys for testing purposes only:
- **Never use these wallets on mainnet**
- **Store private keys securely**
- **Use only for development/testing**
- **Generate new wallets for production**

## Customization

To modify the distribution strategy, edit the `distribution_plan` in the `distribute_devices_optimally()` method:

```python
distribution_plan = {
    1: 45,  # 45 wallets with 1 device each
    2: 8,   # 8 wallets with 2 devices each  
    3: 2,   # 2 wallets with 3 devices each
}
```

## Next Steps

1. Review the generated CSV files
2. Import wallet data into your Cartesi IoT system  
3. Configure paymaster to cover transaction costs
4. Begin IoT data simulation with realistic ownership patterns 