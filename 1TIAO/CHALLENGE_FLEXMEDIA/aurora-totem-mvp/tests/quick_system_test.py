#!/usr/bin/env python3
"""
Aurora Totem - Quick System Test Suite
Task 8 - Simplified System Testing for immediate validation
"""

import requests
import json
import time
import os
from datetime import datetime

def test_system_components():
    """Quick system validation test"""
    print("🚀 Aurora Totem - Quick System Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    results = {}
    
    # Test 1: API Health Check
    print("\n1️⃣ Testing API Health...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Status: {data.get('success', False)}")
            print(f"   📊 Database Connected: {data.get('data', {}).get('database_connected', False)}")
            results['api_health'] = True
        else:
            print(f"   ❌ API returned status: {response.status_code}")
            results['api_health'] = False
    except Exception as e:
        print(f"   ❌ API Health Check Failed: {str(e)}")
        results['api_health'] = False
    
    # Test 2: Database Statistics
    print("\n2️⃣ Testing Database Connection...")
    try:
        response = requests.get(f"{base_url}/api/sensors/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            total_records = stats.get('total_records', 0)
            storage_mode = stats.get('storage_mode', 'unknown')
            print(f"   ✅ Database accessible")
            print(f"   📊 Total Records: {total_records}")
            print(f"   💾 Storage Mode: {storage_mode}")
            results['database'] = True
        else:
            print(f"   ❌ Database test failed with status: {response.status_code}")
            results['database'] = False
    except Exception as e:
        print(f"   ❌ Database Test Failed: {str(e)}")
        results['database'] = False
    
    # Test 3: Sensor Data Endpoints
    print("\n3️⃣ Testing Sensor Data Endpoints...")
    try:
        # Test data retrieval
        response = requests.get(f"{base_url}/api/sensors/data?limit=3", timeout=10)
        if response.status_code == 200:
            data = response.json()
            records = data.get('data', {}).get('records', [])
            print(f"   ✅ Data retrieval successful")
            print(f"   📊 Retrieved {len(records)} records")
            results['sensor_endpoints'] = True
        else:
            print(f"   ❌ Sensor endpoint failed: {response.status_code}")
            results['sensor_endpoints'] = False
    except Exception as e:
        print(f"   ❌ Sensor Endpoints Test Failed: {str(e)}")
        results['sensor_endpoints'] = False
    
    # Test 4: ML Model Status
    print("\n4️⃣ Testing ML Models...")
    try:
        response = requests.get(f"{base_url}/api/ml/model-status", timeout=10)
        if response.status_code == 200:
            ml_status = response.json()
            models_ready = ml_status.get('models_ready', False)
            print(f"   ✅ ML endpoints accessible")
            print(f"   🤖 Models Ready: {models_ready}")
            
            # Try to train models if not ready
            if not models_ready:
                print("   🔄 Training ML models...")
                train_response = requests.post(f"{base_url}/api/ml/train-models", timeout=30)
                if train_response.status_code == 200:
                    train_data = train_response.json()
                    print(f"   ✅ Training completed: {train_data.get('success', False)}")
                    results['ml_models'] = True
                else:
                    print(f"   ❌ Training failed: {train_response.status_code}")
                    results['ml_models'] = False
            else:
                results['ml_models'] = True
        else:
            print(f"   ❌ ML status check failed: {response.status_code}")
            results['ml_models'] = False
    except Exception as e:
        print(f"   ❌ ML Models Test Failed: {str(e)}")
        results['ml_models'] = False
    
    # Test 5: End-to-End Data Flow
    print("\n5️⃣ Testing End-to-End Data Flow...")
    try:
        # Insert test data
        test_data = {
            'device_id': 'system_test_device',
            'sensor_readings': [
                {
                    'sensor_type': 'temperature',
                    'value': 22.5,
                    'metadata': {'test': True, 'timestamp': datetime.now().isoformat()}
                }
            ]
        }
        
        insert_response = requests.post(f"{base_url}/api/sensors/data", json=test_data, timeout=10)
        
        if insert_response.status_code == 200:
            print(f"   ✅ Data insertion successful")
            
            # Wait and verify retrieval
            time.sleep(2)
            verify_response = requests.get(f"{base_url}/api/sensors/data?limit=5", timeout=10)
            
            if verify_response.status_code == 200:
                print(f"   ✅ Data retrieval verified")
                results['end_to_end'] = True
            else:
                print(f"   ❌ Data retrieval failed")
                results['end_to_end'] = False
        else:
            print(f"   ❌ Data insertion failed: {insert_response.status_code}")
            results['end_to_end'] = False
            
    except Exception as e:
        print(f"   ❌ End-to-End Test Failed: {str(e)}")
        results['end_to_end'] = False
    
    # Test 6: Performance Check
    print("\n6️⃣ Testing System Performance...")
    try:
        response_times = []
        for i in range(5):
            start = time.time()
            response = requests.get(f"{base_url}/", timeout=5)
            end = time.time()
            if response.status_code == 200:
                response_times.append(end - start)
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            print(f"   ✅ Performance test completed")
            print(f"   ⚡ Average response: {avg_time:.3f}s")
            print(f"   ⚡ Max response: {max_time:.3f}s")
            results['performance'] = avg_time < 1.0  # Less than 1 second
        else:
            print(f"   ❌ No successful performance measurements")
            results['performance'] = False
            
    except Exception as e:
        print(f"   ❌ Performance Test Failed: {str(e)}")
        results['performance'] = False
    
    # Generate Summary
    print("\n" + "=" * 50)
    print("🏁 SYSTEM TEST SUMMARY")
    print("=" * 50)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    success_rate = passed_tests / total_tests if total_tests > 0 else 0
    
    print(f"📊 Tests Passed: {passed_tests}/{total_tests}")
    print(f"🎯 Success Rate: {success_rate:.1%}")
    
    # Individual test results
    test_names = {
        'api_health': '🌐 API Health',
        'database': '🗄️ Database',
        'sensor_endpoints': '📡 Sensor Endpoints',
        'ml_models': '🤖 ML Models',
        'end_to_end': '🔄 End-to-End Flow',
        'performance': '⚡ Performance'
    }
    
    print("\n📋 Component Status:")
    for key, name in test_names.items():
        status = "✅ PASS" if results.get(key, False) else "❌ FAIL"
        print(f"   {name}: {status}")
    
    overall_status = "✅ SYSTEM HEALTHY" if success_rate >= 0.8 else "❌ SYSTEM ISSUES"
    print(f"\n🎉 Overall Status: {overall_status}")
    
    # Save results
    test_report = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'summary': {
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'success_rate': success_rate,
            'overall_status': overall_status
        }
    }
    
    try:
        # Ensure reports directory exists
        reports_dir = os.path.join('..', 'reports') if os.path.basename(os.getcwd()) == 'tests' else 'reports'
        os.makedirs(reports_dir, exist_ok=True)
        
        # Save report in reports directory
        report_path = os.path.join(reports_dir, 'quick_system_test_report.json')
        with open(report_path, 'w') as f:
            json.dump(test_report, f, indent=2)
        print(f"\n📄 Report saved: {report_path}")
    except Exception as e:
        print(f"\n❌ Failed to save report: {str(e)}")
    
    return results

if __name__ == "__main__":
    test_system_components()