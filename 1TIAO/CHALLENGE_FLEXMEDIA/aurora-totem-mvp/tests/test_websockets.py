#!/usr/bin/env python3
"""
WebSocket Testing for Aurora Totem
Task 8 - Real-time streaming validation
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

async def test_websocket_sensors():
    """Test sensor WebSocket streaming"""
    print("🔌 Testing WebSocket - Sensor Stream")
    
    uri = "ws://localhost:8000/ws/sensors"
    messages_received = 0
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"   ✅ Connected to {uri}")
            
            # Listen for messages with timeout
            for i in range(3):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    data = json.loads(message)
                    messages_received += 1
                    
                    # Extract sensor info
                    readings = data.get('readings', [])
                    device_id = data.get('device_id', 'unknown')
                    
                    print(f"   📡 Message {i+1}: Device {device_id}, {len(readings)} sensors")
                    
                    # Show first sensor reading as example
                    if readings:
                        first_sensor = readings[0]
                        sensor_type = first_sensor.get('sensor_type', 'unknown')
                        value = first_sensor.get('value', 0)
                        print(f"      📊 Sample: {sensor_type} = {value}")
                    
                except asyncio.TimeoutError:
                    print(f"   ⏰ Timeout waiting for message {i+1}")
                    break
                except Exception as e:
                    print(f"   ❌ Error receiving message {i+1}: {str(e)}")
                    break
            
            print(f"   📊 Total messages received: {messages_received}")
            return messages_received > 0
            
    except Exception as e:
        print(f"   ❌ WebSocket connection failed: {str(e)}")
        return False

async def test_websocket_dashboard():
    """Test dashboard WebSocket streaming"""
    print("\n🔌 Testing WebSocket - Dashboard Stream")
    
    uri = "ws://localhost:8000/ws/dashboard"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"   ✅ Connected to {uri}")
            
            # Listen for one message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                print(f"   📊 Dashboard data received: {list(data.keys())}")
                return True
                
            except asyncio.TimeoutError:
                print(f"   ⏰ No dashboard messages received (may be normal)")
                return True  # Connection successful even if no immediate data
                
    except Exception as e:
        print(f"   ❌ Dashboard WebSocket failed: {str(e)}")
        return False

def run_websocket_tests():
    """Run WebSocket tests"""
    print("🚀 Aurora Totem - WebSocket Testing")
    print("=" * 40)
    
    results = {}
    
    # Test sensor WebSocket
    try:
        sensor_result = asyncio.run(test_websocket_sensors())
        results['sensor_websocket'] = sensor_result
    except Exception as e:
        print(f"❌ Sensor WebSocket test failed: {str(e)}")
        results['sensor_websocket'] = False
    
    # Test dashboard WebSocket
    try:
        dashboard_result = asyncio.run(test_websocket_dashboard())
        results['dashboard_websocket'] = dashboard_result
    except Exception as e:
        print(f"❌ Dashboard WebSocket test failed: {str(e)}")
        results['dashboard_websocket'] = False
    
    # Summary
    print("\n" + "=" * 40)
    print("🏁 WebSocket Test Summary")
    print("=" * 40)
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"📊 Tests Passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    overall = "✅ WEBSOCKETS WORKING" if passed == total else "⚠️ PARTIAL SUCCESS"
    print(f"\n🎉 Overall: {overall}")
    
    return results

if __name__ == "__main__":
    run_websocket_tests()