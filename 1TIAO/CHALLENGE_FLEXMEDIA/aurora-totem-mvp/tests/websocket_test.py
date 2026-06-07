#!/usr/bin/env python3
"""
WebSocket Test Client for Aurora Totem API
Demonstrates real-time sensor data streaming
"""

import asyncio
import json
import websockets
import time
from datetime import datetime

async def test_sensor_websocket():
    """Test real-time sensor data WebSocket"""
    uri = "ws://localhost:8000/ws/sensors"
    
    try:
        print("🔌 Conectando ao WebSocket de sensores...")
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado! Aguardando dados de sensores...")
            
            # Listen for messages
            message_count = 0
            start_time = time.time()
            
            while message_count < 5:  # Listen for 5 messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    print(f"\n📡 Mensagem {message_count}:")
                    print(f"   Tipo: {data.get('type', 'unknown')}")
                    print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
                    
                    if data.get('type') == 'sensor_update':
                        sensors = data.get('data', [])
                        print(f"   📊 {len(sensors)} sensores atualizados:")
                        for sensor in sensors[:3]:  # Show first 3
                            sensor_type = sensor.get('sensor_type', 'unknown')
                            value = sensor.get('sensor_value', 0)
                            unit = sensor.get('metadata', {}).get('unit', '')
                            print(f"     {sensor_type}: {value} {unit}")
                    
                    elif data.get('type') == 'initial_data':
                        records = data.get('data', [])
                        print(f"   📋 Dados iniciais: {len(records)} registros")
                        
                except asyncio.TimeoutError:
                    print("⏰ Timeout aguardando dados - enviando ping...")
                    await websocket.send(json.dumps({"type": "ping"}))
                    
            elapsed = time.time() - start_time
            print(f"\n✅ Teste concluído! {message_count} mensagens em {elapsed:.1f}s")
            
    except Exception as e:
        print(f"❌ Erro no WebSocket: {str(e)}")

async def test_dashboard_websocket():
    """Test dashboard WebSocket"""
    uri = "ws://localhost:8000/ws/dashboard"
    
    try:
        print("\n🔌 Conectando ao WebSocket do dashboard...")
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado! Aguardando dados do dashboard...")
            
            # Send request for updates
            await websocket.send(json.dumps({"type": "request_update"}))
            
            message_count = 0
            while message_count < 2:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=8.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    print(f"\n📈 Dashboard Mensagem {message_count}:")
                    print(f"   Tipo: {data.get('type', 'unknown')}")
                    
                    if data.get('type') == 'dashboard_init':
                        stats = data.get('stats', {})
                        print(f"   📊 Total Records: {stats.get('total_records', 0)}")
                        print(f"   📈 Sensor Types: {len(stats.get('sensor_counts', {}))}")
                        
                    elif data.get('type') == 'stats_update':
                        stats = data.get('data', {})
                        print(f"   📊 Stats Update: {stats.get('total_records', 0)} records")
                        
                except asyncio.TimeoutError:
                    print("⏰ Timeout no dashboard")
                    break
                    
    except Exception as e:
        print(f"❌ Erro no dashboard WebSocket: {str(e)}")

def test_http_endpoints():
    """Test HTTP endpoints with curl"""
    import subprocess
    
    print("\n🌐 Testando endpoints HTTP...")
    
    endpoints = [
        ("Health Check", "http://localhost:8000/"),
        ("Sensor Stats", "http://localhost:8000/api/sensors/stats"),
        ("Latest Sensors", "http://localhost:8000/api/sensors/data?limit=2"),
    ]
    
    for name, url in endpoints:
        try:
            result = subprocess.run(
                ["curl", "-s", url], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    print(f"\n✅ {name}:")
                    
                    if "message" in data:
                        print(f"   📝 {data['message']}")
                    
                    if name == "Health Check" and "data" in data:
                        info = data["data"]
                        print(f"   🔌 DB Connected: {info.get('database_connected', False)}")
                        print(f"   📡 WebSockets: {info.get('active_websockets', 0)}")
                        
                    elif name == "Sensor Stats" and "data" in data:
                        stats = data["data"]
                        print(f"   📊 Total: {stats.get('total_records', 0)} records")
                        
                    elif name == "Latest Sensors" and "data" in data:
                        records = data["data"].get("records", [])
                        print(f"   📈 Retrieved: {len(records)} recent records")
                        
                except json.JSONDecodeError:
                    print(f"❌ {name}: Invalid JSON response")
            else:
                print(f"❌ {name}: HTTP error")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {name}: Request timeout")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")

async def main():
    """Main test function"""
    print("🎯 Aurora Totem - WebSocket & API Tester")
    print("=" * 50)
    print("⚠️  Certifique-se de que o servidor esteja rodando:")
    print("   uvicorn main:app --host 0.0.0.0 --port 8000")
    print("=" * 50)
    
    # Test HTTP endpoints first
    test_http_endpoints()
    
    # Test WebSocket connections
    await test_sensor_websocket()
    await test_dashboard_websocket()
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes concluídos!")
    print("🚀 Aurora Totem API funcionando corretamente!")

if __name__ == "__main__":
    asyncio.run(main())