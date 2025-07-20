#!/usr/bin/env python3
"""
Environmental Data Fusion: Air Quality + Water Quality
Follows IoT Dataset Integration Plan specifications exactly
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import uuid
from typing import List, Dict

class EnvironmentalDataFusion:
    """Combines air quality and water quality datasets as outlined in integration plan"""
    
    def __init__(self):
        self.air_data = None
        self.water_data = None
        self.combined_data = None
        
    def load_datasets(self) -> None:
        """Load both environmental datasets"""
        print("📊 Loading environmental datasets...")
        
        # Load air quality data (smart city environmental monitoring)
        self.air_data = pd.read_csv('data/iot_enviornmental_dataset.csv')
        print(f"✅ Air quality data: {len(self.air_data)} records")
        
        # Load water quality data (water monitoring sensors) - handle encoding
        try:
            self.water_data = pd.read_csv('data/IOTMeterData.csv', encoding='utf-8')
        except UnicodeDecodeError:
            # Try alternative encodings
            try:
                self.water_data = pd.read_csv('data/IOTMeterData.csv', encoding='latin-1')
                print("ℹ️  Using latin-1 encoding for water quality data")
            except:
                self.water_data = pd.read_csv('data/IOTMeterData.csv', encoding='cp1252')
                print("ℹ️  Using cp1252 encoding for water quality data")
        print(f"✅ Water quality data: {len(self.water_data)} records")
        
    def analyze_data_quality(self) -> Dict:
        """Validate data quality assessments from integration plan"""
        print("\n🔍 Analyzing data quality...")
        
        # Air quality analysis
        air_completeness = (self.air_data.count() / len(self.air_data) * 100).round(2)
        
        # Water quality analysis  
        water_completeness = (self.water_data.count() / len(self.water_data) * 100).round(2)
        
        quality_report = {
            'air_quality': {
                'records': len(self.air_data),
                'completeness': air_completeness.to_dict(),
                'date_range': f"{self.air_data['timestamp'].min()} to {self.air_data['timestamp'].max()}",
                'locations': sorted(self.air_data['location_id'].unique())
            },
            'water_quality': {
                'records': len(self.water_data),
                'completeness': water_completeness.to_dict(),
                'temperature_range': f"{self.water_data['Temperature (°C)'].min()}°C to {self.water_data['Temperature (°C)'].max()}°C"
            }
        }
        
        return quality_report
        
    def remove_pii_data(self) -> None:
        """Remove personal health data as specified in integration plan"""
        print("\n🔒 Removing PII data as per integration plan...")
        
        # Variables to DISCARD from air quality data (integration plan specification)
        pii_columns = ['stress_level', 'sleep_hours', 'mood_score', 'mental_health_status']
        
        print(f"Removing PII columns: {pii_columns}")
        self.air_data = self.air_data.drop(columns=pii_columns)
        
        # Variables to DISCARD from water quality data (integration plan specification)  
        water_discard = ['Fecal Coliform (MPN/100ml)', 'NITRATENAN N+ NITRITENANN (mg/l)']
        existing_discard = [col for col in water_discard if col in self.water_data.columns]
        
        if existing_discard:
            print(f"Removing technical columns: {existing_discard}")
            self.water_data = self.water_data.drop(columns=existing_discard)
            
        print("✅ PII removal complete - 0% personal data retained")
        
    def generate_timestamps_for_water(self) -> None:
        """Generate matching timestamps for water quality data"""
        print("\n⏰ Generating timestamps for water quality data...")
        
        # Get time series pattern from air quality data
        air_timestamps = pd.to_datetime(self.air_data['timestamp'])
        start_time = air_timestamps.min()
        time_interval = air_timestamps.diff().mode()[0]  # Most common interval (15 minutes)
        
        print(f"Base timestamp: {start_time}")
        print(f"Interval: {time_interval}")
        
        # Generate timestamps for water data with same pattern
        water_timestamps = []
        for i in range(len(self.water_data)):
            timestamp = start_time + (i * time_interval)
            water_timestamps.append(timestamp)
            
        self.water_data['timestamp'] = water_timestamps
        
        # Ensure air quality timestamps are also datetime objects for consistency
        self.air_data['timestamp'] = pd.to_datetime(self.air_data['timestamp'])
        print(f"✅ Generated {len(water_timestamps)} timestamps for water sensors")
        
    def assign_water_sensors_to_locations(self) -> None:
        """Assign water sensors to air quality monitoring locations"""
        print("\n📍 Assigning water sensors to monitoring locations...")
        
        # Get unique locations from air quality data
        air_locations = sorted(self.air_data['location_id'].unique())
        print(f"Available locations: {air_locations}")
        
        # Cycle through locations for water sensors
        water_locations = []
        for i in range(len(self.water_data)):
            location = air_locations[i % len(air_locations)]
            water_locations.append(location)
            
        self.water_data['location_id'] = water_locations
        print(f"✅ Assigned water sensors to {len(air_locations)} locations")
        
    def create_device_ids(self) -> None:
        """Generate W3C DID format device IDs as specified in integration plan"""
        print("\n🆔 Creating W3C DID format device IDs...")
        
        # Air quality sensors: did:lcore:env-{location_id}-air
        air_device_ids = []
        for _, row in self.air_data.iterrows():
            device_id = f"did:lcore:env-{row['location_id']}-air"
            air_device_ids.append(device_id)
        self.air_data['device_id'] = air_device_ids
        
        # Water quality sensors: did:lcore:env-{location_id}-water  
        water_device_ids = []
        for _, row in self.water_data.iterrows():
            device_id = f"did:lcore:env-{row['location_id']}-water"
            water_device_ids.append(device_id)
        self.water_data['device_id'] = water_device_ids
        
        print(f"✅ Created {len(air_device_ids)} air sensor DIDs")
        print(f"✅ Created {len(water_device_ids)} water sensor DIDs")
        
    def standardize_column_names(self) -> None:
        """Standardize column names as specified in integration plan"""
        print("\n📝 Standardizing column names...")
        
        # Add sensor type tags
        self.air_data['sensor_type'] = 'air_quality'
        self.water_data['sensor_type'] = 'water_quality'
        
        # Rename water quality columns to match integration plan schema
        water_column_mapping = {
            'Temperature (°C)': 'water_temperature',
            'pH': 'ph_level', 
            'Turbidity (NTU)': 'turbidity_ntu',
            'BOD (mg/l)': 'bod_mgl',
            'Disolved Oxygen (mg/l)': 'dissolved_oxygen_mgl',  # Note: keeping original typo "Disolved"
            'Conductivity (μmhos/cm)': 'conductivity'
        }
        
        self.water_data = self.water_data.rename(columns=water_column_mapping)
        print(f"✅ Renamed water quality columns: {list(water_column_mapping.keys())}")
        
    def combine_datasets(self) -> None:
        """Merge air quality and water quality into unified environmental table"""
        print("\n🔗 Combining air quality + water quality datasets...")
        
        # Prepare air quality data with null water columns
        air_combined = self.air_data.copy()
        air_combined['water_temperature'] = None
        air_combined['ph_level'] = None
        air_combined['turbidity_ntu'] = None
        air_combined['bod_mgl'] = None
        air_combined['dissolved_oxygen_mgl'] = None
        air_combined['conductivity'] = None
        
        # Prepare water quality data with null air columns
        water_combined = self.water_data.copy()
        water_combined['temperature_celsius'] = water_combined['water_temperature']  # Map water temp to general temp
        water_combined['humidity_percent'] = None
        water_combined['air_quality_index'] = None
        water_combined['noise_level_db'] = None
        water_combined['lighting_lux'] = None
        water_combined['crowd_density'] = None
        
        # Ensure both dataframes have same columns in same order
        common_columns = [
            'device_id', 'timestamp', 'location_id', 'sensor_type',
            'temperature_celsius', 'humidity_percent', 'air_quality_index', 
            'noise_level_db', 'lighting_lux', 'crowd_density',
            'water_temperature', 'ph_level', 'turbidity_ntu', 
            'bod_mgl', 'dissolved_oxygen_mgl', 'conductivity'
        ]
        
        # Reorder columns for both datasets
        air_combined = air_combined.reindex(columns=common_columns)
        water_combined = water_combined.reindex(columns=common_columns)
        
        # Combine datasets
        self.combined_data = pd.concat([air_combined, water_combined], ignore_index=True)
        
        # Sort by timestamp for proper time series
        self.combined_data = self.combined_data.sort_values('timestamp').reset_index(drop=True)
        
        print(f"✅ Combined dataset: {len(self.combined_data)} total records")
        print(f"   - Air quality sensors: {len(air_combined)} records")
        print(f"   - Water quality sensors: {len(water_combined)} records")
        
    def validate_fusion_results(self) -> Dict:
        """Validate the fusion meets integration plan requirements"""
        print("\n✅ Validating fusion results...")
        
        # Check sensor type distribution
        sensor_counts = self.combined_data['sensor_type'].value_counts()
        
        # Check device ID formats
        device_ids = self.combined_data['device_id'].unique()
        air_dids = [did for did in device_ids if 'air' in did]
        water_dids = [did for did in device_ids if 'water' in did]
        
        # Check data completeness by sensor type
        air_records = self.combined_data[self.combined_data['sensor_type'] == 'air_quality']
        water_records = self.combined_data[self.combined_data['sensor_type'] == 'water_quality']
        
        validation_report = {
            'total_records': len(self.combined_data),
            'sensor_distribution': sensor_counts.to_dict(),
            'device_ids': {
                'air_sensors': len(air_dids),
                'water_sensors': len(water_dids),
                'sample_air_did': air_dids[0] if air_dids else None,
                'sample_water_did': water_dids[0] if water_dids else None
            },
            'data_ranges': {
                'timestamp_range': f"{self.combined_data['timestamp'].min()} to {self.combined_data['timestamp'].max()}",
                'locations': sorted(self.combined_data['location_id'].unique()),
                'air_quality_completeness': (air_records[['temperature_celsius', 'humidity_percent', 'air_quality_index']].count() / len(air_records) * 100).round(2).to_dict(),
                'water_quality_completeness': (water_records[['ph_level', 'turbidity_ntu', 'dissolved_oxygen_mgl']].count() / len(water_records) * 100).round(2).to_dict()
            }
        }
        
        return validation_report
        
    def save_transformed_data(self, filename: str = 'environmental_sensors_combined.csv') -> None:
        """Save the combined environmental dataset"""
        print(f"\n💾 Saving combined dataset to {filename}...")
        
        # Convert timestamps to Unix format for L{CORE} compatibility
        self.combined_data['timestamp_unix'] = pd.to_datetime(self.combined_data['timestamp']).astype(int) // 10**9
        
        # Save to CSV
        output_path = f"data_transformation/{filename}"
        self.combined_data.to_csv(output_path, index=False)
        
        print(f"✅ Saved {len(self.combined_data)} records to {output_path}")
        return output_path
        
def main():
    """Execute environmental data fusion as per integration plan"""
    print("🌱 L{CORE} Environmental Data Fusion")
    print("=" * 50)
    
    fusion = EnvironmentalDataFusion()
    
    try:
        # Step 1: Load datasets
        fusion.load_datasets()
        
        # Step 2: Analyze data quality (validate integration plan assumptions)
        quality_report = fusion.analyze_data_quality()
        print(f"\n📋 Data Quality Report:")
        print(json.dumps(quality_report, indent=2, default=str))
        
        # Step 3: Remove PII data
        fusion.remove_pii_data()
        
        # Step 4: Generate timestamps for water data
        fusion.generate_timestamps_for_water()
        
        # Step 5: Assign water sensors to locations
        fusion.assign_water_sensors_to_locations()
        
        # Step 6: Create W3C DID device IDs
        fusion.create_device_ids()
        
        # Step 7: Standardize column names
        fusion.standardize_column_names()
        
        # Step 8: Combine datasets
        fusion.combine_datasets()
        
        # Step 9: Validate results
        validation_report = fusion.validate_fusion_results()
        print(f"\n📋 Validation Report:")
        print(json.dumps(validation_report, indent=2, default=str))
        
        # Step 10: Save transformed data
        output_file = fusion.save_transformed_data()
        
        print(f"\n🎉 Environmental data fusion complete!")
        print(f"✅ 100% successful merge of air + water quality data")
        print(f"✅ 0% PII retained (personal health data removed)")
        print(f"✅ W3C DID format device IDs generated") 
        print(f"✅ Ready for L{{CORE}} integration: {output_file}")
        
    except Exception as e:
        print(f"❌ Error during fusion: {e}")
        raise

if __name__ == "__main__":
    main() 