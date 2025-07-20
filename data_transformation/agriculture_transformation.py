#!/usr/bin/env python3
"""
Agriculture Time-Series Transformation: Static Research Data → IoT Sensors
Follows IoT Dataset Integration Plan specifications exactly
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class AgricultureTransformation:
    """Convert static plant research data to IoT time-series format"""
    
    def __init__(self):
        self.raw_data = None
        self.transformed_data = None
        
    def load_dataset(self) -> None:
        """Load agriculture research dataset"""
        print("🌱 Loading agriculture research dataset...")
        
        try:
            self.raw_data = pd.read_csv('data/IoT Agriculture.csv')
            print(f"✅ Agriculture data: {len(self.raw_data)} research records")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
            
    def analyze_data_structure(self) -> dict:
        """Analyze dataset structure per integration plan"""
        print("\n🔍 Analyzing agriculture data structure...")
        
        # Check columns and data ranges
        columns = list(self.raw_data.columns)
        sample_plot_ids = self.raw_data['Random'].value_counts().head(10)
        class_distribution = self.raw_data['Class'].value_counts()
        
        analysis = {
            'total_records': len(self.raw_data),
            'columns': columns,
            'plot_distribution': sample_plot_ids.to_dict(),
            'class_distribution': class_distribution.to_dict(),
            'data_ranges': {
                'chlorophyll': f"{self.raw_data.iloc[:, 1].min():.2f} to {self.raw_data.iloc[:, 1].max():.2f}",
                'height_rate': f"{self.raw_data.iloc[:, 2].min():.2f} to {self.raw_data.iloc[:, 2].max():.2f}",
                'leaf_area': f"{self.raw_data.iloc[:, 4].min():.2f} to {self.raw_data.iloc[:, 4].max():.2f}"
            }
        }
        
        return analysis
        
    def remove_redundant_variables(self) -> None:
        """Remove variables marked as DISCARD in integration plan"""
        print("\n🗑️ Removing redundant variables per integration plan...")
        
        # Variables to DISCARD from integration plan
        discard_columns = [
            'Average wet weight of the root (AWWR)',  # Redundant with dry weight
            'Average dry weight of vegetative plants (ADWV)',  # Redundant with vegetative weight
            'Percentage of dry matter for root growth (PDMRG)'  # Too specific for demo
        ]
        
        # Check which columns actually exist (column names might be truncated)
        existing_discard = []
        for col in discard_columns:
            # Check for partial matches since CSV headers might be truncated
            matching_cols = [c for c in self.raw_data.columns if 'wet weight of the root' in c or 
                           'dry weight of vegetative' in c or 'root growth' in c]
            existing_discard.extend(matching_cols)
            
        if existing_discard:
            print(f"Removing columns: {existing_discard}")
            self.raw_data = self.raw_data.drop(columns=existing_discard, errors='ignore')
        
        print(f"✅ Redundant variable removal complete")
        
    def standardize_column_names(self) -> None:
        """Standardize variable names as specified in integration plan"""
        print("\n📝 Standardizing column names...")
        
        # Column mapping from integration plan
        column_mapping = {
            'Random': 'plot_id',
            'Average  of chlorophyll in the plant (ACHP)': 'chlorophyll_avg',
            'Plant height rate (PHR)': 'height_rate', 
            'Average wet weight of the growth vegetative (AWWGV)': 'wet_weight_vegetative',
            'Average leaf area of the plant (ALAP)': 'leaf_area_avg',
            'Average number of plant leaves (ANPL)': 'leaf_count_avg',
            'Average root diameter (ARD)': 'root_diameter_avg',
            'Average dry weight of the root (ADWR)': 'root_dry_weight',
            'Percentage of dry matter for vegetative growth (PDMVG)': 'dry_matter_vegetative',
            'Average root length (ARL)': 'root_length_avg',
            'Class': 'plant_class'
        }
        
        # Apply mappings for columns that exist
        actual_mapping = {}
        for old_name, new_name in column_mapping.items():
            if old_name in self.raw_data.columns:
                actual_mapping[old_name] = new_name
            else:
                # Try partial matching for truncated column names
                matching = [col for col in self.raw_data.columns if old_name[:20] in col]
                if matching:
                    actual_mapping[matching[0]] = new_name
                    
        self.raw_data = self.raw_data.rename(columns=actual_mapping)
        print(f"✅ Renamed {len(actual_mapping)} columns")
        
    def generate_iot_timestamps(self) -> None:
        """Generate realistic IoT timestamps for plant monitoring"""
        print("\n⏰ Generating IoT time-series timestamps...")
        
        # Parameters for realistic agricultural monitoring
        # Agricultural sensors typically collect data multiple times per day
        measurement_interval_hours = 6  # Every 6 hours (4 readings per day)
        start_date = datetime(2024, 3, 1)  # Start of growing season
        
        print(f"Measurement interval: Every {measurement_interval_hours} hours")
        print(f"Start date: {start_date}")
        
        # Generate timestamps
        timestamps = []
        for i in range(len(self.raw_data)):
            timestamp = start_date + timedelta(hours=i * measurement_interval_hours)
            timestamps.append(timestamp)
            
        self.raw_data['timestamp'] = timestamps
        
        # Convert to Unix timestamp for L{CORE} compatibility
        self.raw_data['timestamp_unix'] = pd.to_datetime(self.raw_data['timestamp']).astype(int) // 10**9
        
        print(f"✅ Generated {len(timestamps)} timestamps")
        print(f"Time range: {timestamps[0]} to {timestamps[-1]}")
        
    def create_device_ids(self) -> None:
        """Generate W3C DID format device IDs per integration plan"""
        print("\n🆔 Creating W3C DID format device IDs...")
        
        # Agricultural sensors: did:lcore:agri-{plot_id}
        device_ids = []
        for _, row in self.raw_data.iterrows():
            device_id = f"did:lcore:agri-{row['plot_id']}"
            device_ids.append(device_id)
            
        self.raw_data['device_id'] = device_ids
        
        unique_devices = self.raw_data['device_id'].nunique()
        print(f"✅ Created {len(device_ids)} device readings from {unique_devices} unique agricultural sensors")
        
    def create_schema_compliant_format(self) -> None:
        """Create L{CORE} agricultural_sensors schema compliant dataset"""
        print("\n🏗️ Creating L{CORE} schema compliant format...")
        
        # Create new dataframe with exact schema columns
        self.transformed_data = pd.DataFrame()
        
        # Required schema fields
        self.transformed_data['device_id'] = self.raw_data['device_id']
        self.transformed_data['owner_address'] = 'PLACEHOLDER_FOR_CARTESI'  # Added during Cartesi ingestion
        self.transformed_data['timestamp'] = self.raw_data['timestamp_unix']
        
        # Agricultural sensor data (mapping to schema)
        self.transformed_data['chlorophyll_avg'] = self.raw_data.get('chlorophyll_avg', np.nan)
        self.transformed_data['height_rate'] = self.raw_data.get('height_rate', np.nan)
        self.transformed_data['wet_weight_vegetative'] = self.raw_data.get('wet_weight_vegetative', np.nan)
        self.transformed_data['leaf_area_avg'] = self.raw_data.get('leaf_area_avg', np.nan)
        self.transformed_data['leaf_count_avg'] = self.raw_data.get('leaf_count_avg', np.nan)
        self.transformed_data['root_diameter_avg'] = self.raw_data.get('root_diameter_avg', np.nan)
        self.transformed_data['root_dry_weight'] = self.raw_data.get('root_dry_weight', np.nan)
        self.transformed_data['dry_matter_vegetative'] = self.raw_data.get('dry_matter_vegetative', np.nan)
        self.transformed_data['root_length_avg'] = self.raw_data.get('root_length_avg', np.nan)
        self.transformed_data['plant_class'] = self.raw_data.get('plant_class', 'unknown')
        
        # Cartesi-generated fields (placeholders)
        self.transformed_data['encrypted_data'] = 'CARTESI_GENERATED'
        self.transformed_data['data_hash'] = 'CARTESI_GENERATED'
        
        print(f"✅ Schema compliant format created: {len(self.transformed_data)} records")
        
    def validate_transformation(self) -> dict:
        """Validate transformation meets integration plan requirements"""
        print("\n✅ Validating agriculture transformation...")
        
        # Check device ID formats
        sample_dids = self.transformed_data['device_id'].head(5).tolist()
        unique_plots = self.transformed_data['device_id'].nunique()
        
        # Check data ranges
        data_ranges = {}
        for col in ['chlorophyll_avg', 'height_rate', 'leaf_area_avg']:
            if col in self.transformed_data.columns:
                data_ranges[col] = {
                    'min': float(self.transformed_data[col].min()),
                    'max': float(self.transformed_data[col].max()),
                    'mean': float(self.transformed_data[col].mean())
                }
        
        # Check timestamp coverage
        timestamps = pd.to_datetime(self.transformed_data['timestamp'], unit='s')
        
        validation_report = {
            'total_records': len(self.transformed_data),
            'unique_agricultural_sensors': unique_plots,
            'sample_device_ids': sample_dids,
            'timestamp_range': f"{timestamps.min()} to {timestamps.max()}",
            'measurement_days': (timestamps.max() - timestamps.min()).days,
            'data_ranges': data_ranges,
            'plant_classes': self.transformed_data['plant_class'].value_counts().to_dict() if 'plant_class' in self.transformed_data.columns else {}
        }
        
        return validation_report
        
    def save_transformed_data(self, filename: str = 'agricultural_sensors_transformed.csv') -> str:
        """Save the transformed agricultural IoT dataset"""
        print(f"\n💾 Saving transformed agricultural dataset...")
        
        output_path = f"data_transformation/{filename}"
        self.transformed_data.to_csv(output_path, index=False)
        
        print(f"✅ Saved {len(self.transformed_data)} agricultural sensor records to {output_path}")
        return output_path

def main():
    """Execute agriculture transformation per integration plan"""
    print("🌾 L{CORE} Agriculture Time-Series Transformation")
    print("=" * 60)
    
    transformer = AgricultureTransformation()
    
    try:
        # Step 1: Load dataset
        transformer.load_dataset()
        
        # Step 2: Analyze structure
        analysis = transformer.analyze_data_structure()
        print(f"\n📋 Data Structure Analysis:")
        print(json.dumps(analysis, indent=2, default=str))
        
        # Step 3: Remove redundant variables
        transformer.remove_redundant_variables()
        
        # Step 4: Standardize column names
        transformer.standardize_column_names()
        
        # Step 5: Generate IoT timestamps
        transformer.generate_iot_timestamps()
        
        # Step 6: Create device IDs
        transformer.create_device_ids()
        
        # Step 7: Create schema compliant format
        transformer.create_schema_compliant_format()
        
        # Step 8: Validate transformation
        validation = transformer.validate_transformation()
        print(f"\n📋 Validation Report:")
        print(json.dumps(validation, indent=2, default=str))
        
        # Step 9: Save transformed data
        output_file = transformer.save_transformed_data()
        
        print(f"\n🎉 Agriculture transformation complete!")
        print(f"✅ Static research data → IoT time-series conversion successful")
        print(f"✅ W3C DID format device IDs generated")
        print(f"✅ {validation['measurement_days']} days of agricultural monitoring data")
        print(f"✅ Ready for L{{CORE}} integration: {output_file}")
        
    except Exception as e:
        print(f"❌ Error during transformation: {e}")
        raise

if __name__ == "__main__":
    main()
