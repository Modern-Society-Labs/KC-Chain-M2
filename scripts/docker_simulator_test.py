#!/usr/bin/env python3
"""
L{CORE} IoT Docker Simulator Test Script
========================================

This script provides a comprehensive test environment for the L{CORE} IoT data transformation
and node integration system. It runs in a Docker container to ensure reproducible testing.

Features:
- Tests all 6 IoT domain transformations
- Validates data integrity and privacy compliance
- Tests L{CORE} node connectivity and GraphQL API
- Generates test reports with performance metrics
"""

import os
import sys
import json
import time
import subprocess
import requests
import sqlite3
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

class IoTSimulatorTest:
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        self.lcore_endpoint = os.getenv('LCORE_NODE_URL', 'http://45.55.204.196:8000/graphql')
        self.test_data_dir = Path('/tmp/simulator_test_data')
        self.test_data_dir.mkdir(exist_ok=True)
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def run_transformation_tests(self):
        """Test all data transformation scripts"""
        self.log("Starting data transformation tests...")
        
        transformations = [
            'environmental_fusion.py',
            'agriculture_transformation.py', 
            'health_privacy_protection.py',
            'network_performance_parsing.py',
            'retail_pii_anonymization.py',
            'weather_unit_conversion.py'
        ]
        
        transformation_results = {}
        
        for script in transformations:
            self.log(f"Testing {script}...")
            try:
                start_time = time.time()
                
                # Run transformation script
                result = subprocess.run([
                    'python3', f'/app/data_transformation/{script}'
                ], capture_output=True, text=True, timeout=300)
                
                execution_time = time.time() - start_time
                
                if result.returncode == 0:
                    transformation_results[script] = {
                        'status': 'PASS',
                        'execution_time': execution_time,
                        'output_lines': len(result.stdout.split('\n'))
                    }
                    self.log(f"✅ {script} completed in {execution_time:.2f}s")
                else:
                    transformation_results[script] = {
                        'status': 'FAIL',
                        'execution_time': execution_time,
                        'error': result.stderr
                    }
                    self.log(f"❌ {script} failed: {result.stderr}", "ERROR")
                    
            except subprocess.TimeoutExpired:
                transformation_results[script] = {
                    'status': 'TIMEOUT',
                    'execution_time': 300,
                    'error': 'Script execution timed out after 5 minutes'
                }
                self.log(f"⏰ {script} timed out", "ERROR")
            except Exception as e:
                transformation_results[script] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
                self.log(f"💥 {script} error: {str(e)}", "ERROR")
        
        self.test_results['transformations'] = transformation_results
        return transformation_results

    def test_lcore_node_connectivity(self):
        """Test connection to L{CORE} node GraphQL endpoint"""
        self.log("Testing L{CORE} node connectivity...")
        
        try:
            # Test basic health check
            response = requests.get(f"{self.lcore_endpoint.replace('/graphql', '/health')}", timeout=10)
            if response.status_code == 200:
                self.log("✅ L{CORE} node health check passed")
                health_status = True
            else:
                self.log(f"❌ Health check failed with status {response.status_code}", "ERROR")
                health_status = False
        except Exception as e:
            self.log(f"❌ Health check error: {str(e)}", "ERROR")
            health_status = False
            
        # Test GraphQL endpoint
        try:
            query = """
            query {
                sensorReadings(limit: 1) {
                    deviceId
                    timestamp
                    sensorData
                }
            }
            """
            
            response = requests.post(
                self.lcore_endpoint,
                json={'query': query},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'sensorReadings' in data['data']:
                    self.log("✅ GraphQL API responding correctly")
                    graphql_status = True
                else:
                    self.log(f"❌ GraphQL response invalid: {data}", "ERROR")
                    graphql_status = False
            else:
                self.log(f"❌ GraphQL request failed with status {response.status_code}", "ERROR")
                graphql_status = False
                
        except Exception as e:
            self.log(f"❌ GraphQL error: {str(e)}", "ERROR")
            graphql_status = False
            
        self.test_results['node_connectivity'] = {
            'health_check': health_status,
            'graphql_api': graphql_status,
            'endpoint': self.lcore_endpoint
        }
        
        return health_status and graphql_status

    def test_data_integrity(self):
        """Test data integrity and privacy compliance"""
        self.log("Testing data integrity and privacy compliance...")
        
        # Look for transformed data files
        data_files = list(Path('/tmp').glob('*_transformed.csv'))
        
        integrity_results = {}
        
        for data_file in data_files:
            self.log(f"Checking data integrity for {data_file.name}...")
            
            try:
                import pandas as pd
                df = pd.read_csv(data_file)
                
                # Basic integrity checks
                total_records = len(df)
                null_count = df.isnull().sum().sum()
                
                # Privacy checks (look for common PII patterns)
                pii_violations = 0
                pii_columns = ['name', 'email', 'phone', 'address', 'ssn', 'customer_name', 'user_id']
                
                for col in df.columns:
                    if any(pii_term in col.lower() for pii_term in pii_columns):
                        pii_violations += 1
                        
                integrity_results[data_file.name] = {
                    'total_records': total_records,
                    'null_values': int(null_count),
                    'pii_violations': pii_violations,
                    'status': 'PASS' if pii_violations == 0 else 'PRIVACY_CONCERN'
                }
                
                if pii_violations == 0:
                    self.log(f"✅ {data_file.name}: {total_records} records, privacy compliant")
                else:
                    self.log(f"⚠️ {data_file.name}: {pii_violations} potential PII violations", "WARNING")
                    
            except Exception as e:
                integrity_results[data_file.name] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
                self.log(f"❌ Error checking {data_file.name}: {str(e)}", "ERROR")
        
        self.test_results['data_integrity'] = integrity_results
        return integrity_results

    def test_device_authentication(self):
        """Test W3C DID device authentication"""
        self.log("Testing W3C DID device authentication...")
        
        # Test DID format validation
        did_patterns = [
            'did:lcore:env-',
            'did:lcore:agri-', 
            'did:lcore:health-',
            'did:lcore:cell-tower-',
            'did:lcore:retail-',
            'did:lcore:weather-'
        ]
        
        did_test_results = {}
        
        try:
            # Try to query available devices from GraphQL
            query = """
            query {
                availableDevices {
                    deviceId
                    deviceType
                    dataPoints
                }
            }
            """
            
            response = requests.post(
                self.lcore_endpoint,
                json={'query': query},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'availableDevices' in data['data']:
                    devices = data['data']['availableDevices']
                    
                    valid_dids = 0
                    total_devices = len(devices)
                    
                    for device in devices:
                        device_id = device.get('deviceId', '')
                        if any(pattern in device_id for pattern in did_patterns):
                            valid_dids += 1
                            
                    did_test_results = {
                        'total_devices': total_devices,
                        'valid_did_format': valid_dids,
                        'compliance_rate': (valid_dids / total_devices * 100) if total_devices > 0 else 0,
                        'status': 'PASS' if valid_dids == total_devices else 'PARTIAL'
                    }
                    
                    self.log(f"✅ DID compliance: {valid_dids}/{total_devices} devices ({did_test_results['compliance_rate']:.1f}%)")
                else:
                    did_test_results = {'status': 'NO_DATA', 'error': 'No device data available'}
                    
            else:
                did_test_results = {'status': 'API_ERROR', 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            did_test_results = {'status': 'ERROR', 'error': str(e)}
            self.log(f"❌ DID authentication test error: {str(e)}", "ERROR")
        
        self.test_results['device_authentication'] = did_test_results
        return did_test_results

    def run_performance_benchmark(self):
        """Run performance benchmarks"""
        self.log("Running performance benchmarks...")
        
        benchmark_results = {}
        
        try:
            # Test query response times
            queries = [
                "{ sensorReadings(limit: 10) { deviceId timestamp } }",
                "{ availableDevices { deviceId deviceType } }",
                "{ sensorTypeStats { sensorType deviceCount } }"
            ]
            
            for i, query in enumerate(queries):
                response_times = []
                
                for _ in range(5):  # Run each query 5 times
                    start_time = time.time()
                    
                    response = requests.post(
                        self.lcore_endpoint,
                        json={'query': query},
                        headers={'Content-Type': 'application/json'},
                        timeout=30
                    )
                    
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        response_times.append(response_time)
                    
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)
                    benchmark_results[f'query_{i+1}'] = {
                        'avg_response_time': avg_response_time,
                        'min_response_time': min(response_times),
                        'max_response_time': max(response_times),
                        'status': 'PASS' if avg_response_time < 5.0 else 'SLOW'
                    }
                    
                    self.log(f"Query {i+1} average response time: {avg_response_time:.3f}s")
                    
        except Exception as e:
            benchmark_results = {'status': 'ERROR', 'error': str(e)}
            self.log(f"❌ Performance benchmark error: {str(e)}", "ERROR")
        
        self.test_results['performance'] = benchmark_results
        return benchmark_results

    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.log("Generating test report...")
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        report = {
            'test_summary': {
                'start_time': self.start_time.isoformat(),
                'total_duration': total_time,
                'test_environment': 'Docker Container',
                'lcore_endpoint': self.lcore_endpoint
            },
            'results': self.test_results
        }
        
        # Calculate overall status
        overall_status = "PASS"
        failed_tests = 0
        total_tests = 0
        
        for test_category, results in self.test_results.items():
            if isinstance(results, dict):
                if test_category == 'transformations':
                    for script, result in results.items():
                        total_tests += 1
                        if result.get('status') != 'PASS':
                            failed_tests += 1
                            overall_status = "FAIL"
                elif results.get('status') in ['FAIL', 'ERROR', 'TIMEOUT']:
                    failed_tests += 1
                    overall_status = "FAIL"
                    
                total_tests += 1
        
        report['test_summary']['overall_status'] = overall_status
        report['test_summary']['passed_tests'] = total_tests - failed_tests
        report['test_summary']['failed_tests'] = failed_tests
        report['test_summary']['total_tests'] = total_tests
        
        # Save report
        report_file = Path('/tmp/iot_simulator_test_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.log(f"Test report saved to {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("L{CORE} IoT SIMULATOR TEST SUMMARY")
        print("="*60)
        print(f"Overall Status: {overall_status}")
        print(f"Tests Passed: {total_tests - failed_tests}/{total_tests}")
        print(f"Total Duration: {total_time:.2f} seconds")
        print(f"L{CORE} Endpoint: {self.lcore_endpoint}")
        print("="*60)
        
        return report

    def run_all_tests(self):
        """Run complete test suite"""
        self.log("Starting L{CORE} IoT Simulator Test Suite...")
        
        # Run all test phases
        self.run_transformation_tests()
        self.test_lcore_node_connectivity()
        self.test_data_integrity()
        self.test_device_authentication()
        self.run_performance_benchmark()
        
        # Generate final report
        report = self.generate_test_report()
        
        return report['test_summary']['overall_status'] == "PASS"


def main():
    """Main test execution"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print(__doc__)
        return
        
    simulator = IoTSimulatorTest()
    
    try:
        success = simulator.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test suite error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 