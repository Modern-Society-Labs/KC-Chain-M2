#!/usr/bin/env python3
"""
Master Script: Execute All IoT Dataset Transformations
Runs all 6 dataset transformations per IoT Dataset Integration Plan
"""
import subprocess
import sys
import os
from datetime import datetime

def run_script(script_name, description):
    """Run a transformation script and report results"""
    print(f"\n{'='*60}")
    print(f"🚀 EXECUTING: {description}")
    print(f"📄 Script: {script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ SUCCESS: {description} completed successfully")
            return True
        else:
            print(f"❌ FAILED: {description}")
            print(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR running {script_name}: {e}")
        return False

def main():
    """Execute all IoT dataset transformations in sequence"""
    print("🎯 L{CORE} IoT Dataset Integration - Master Transformation Script")
    print("=" * 80)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("�� Executing Phase 1: Data Transformation (All 6 Datasets)")
    
    # Change to data_transformation directory
    os.chdir('data_transformation')
    
    # Define transformation sequence per integration plan
    transformations = [
        ("environmental_fusion.py", "Environmental Data Fusion (Air + Water Quality)"),
        ("agriculture_transformation.py", "Agriculture Time-Series Generation"),
        ("health_privacy_protection.py", "Health Data Privacy Protection"),
        ("network_performance_parsing.py", "Network Performance String Parsing"),
        ("retail_pii_anonymization.py", "Retail Sales PII Anonymization + KC Neighborhoods"),
        ("weather_unit_conversion.py", "Weather Data Unit Conversion (F→C)")
    ]
    
    # Execute transformations
    results = []
    for script, description in transformations:
        success = run_script(script, description)
        results.append((script, description, success))
    
    # Summary report
    print(f"\n{'='*80}")
    print("📊 TRANSFORMATION SUMMARY REPORT")
    print(f"{'='*80}")
    
    successful = 0
    failed = 0
    
    for script, description, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {description}")
        if success:
            successful += 1
        else:
            failed += 1
    
    print(f"\n📈 OVERALL RESULTS:")
    print(f"   • Successful transformations: {successful}/{len(transformations)}")
    print(f"   • Failed transformations: {failed}/{len(transformations)}")
    print(f"   • Success rate: {(successful/len(transformations)*100):.1f}%")
    
    if successful == len(transformations):
        print(f"\n🎉 PHASE 1 COMPLETE: ALL DATASETS SUCCESSFULLY TRANSFORMED!")
        print(f"✅ Environmental fusion (Air + Water quality)")
        print(f"✅ Agriculture time-series generation")
        print(f"✅ Health privacy protection (0% location data)")
        print(f"✅ Network string parsing (dBm, ms, Mbps)")
        print(f"✅ Retail PII anonymization + Kansas City")
        print(f"✅ Weather unit conversion (F→C)")
        print(f"\n🚀 Ready for Phase 2: L{{CORE}} Integration!")
    else:
        print(f"\n⚠️  Some transformations failed. Review errors above.")
    
    print(f"\n📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
