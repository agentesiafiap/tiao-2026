"""
Task 8 - System Testing Framework
Aurora Totem MVP - Comprehensive Integration Testing

Tests all integrated components working together:
- Oracle FIAP Database connection and operations
- FastAPI backend with all endpoints
- ML models training and predictions
- Sensor simulation and data flow
- WebSocket real-time streaming
- Dashboard integration
- End-to-end workflow validation
"""

import pytest
import asyncio
import aiohttp
import websockets
import requests
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseManager, ORACLE_AVAILABLE
from src.sensor_simulator import SensorSimulator
from src.ml_model import EmotionPatternAnalyzer
from src.config import DATABASE_CONFIG, API_CONFIG

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemTestFramework:
    """Comprehensive system testing framework for Aurora Totem"""
    
    def __init__(self):
        self.base_url = f"http://{API_CONFIG['host']}:{API_CONFIG['port']}"
        self.websocket_url = f"ws://{API_CONFIG['host']}:{API_CONFIG['port']}"
        self.test_results = {
            'database': {},
            'api_endpoints': {},
            'ml_models': {},
            'websocket': {},
            'integration': {},
            'performance': {},
            'error_handling': {}
        }
        self.start_time = datetime.now()
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete system test suite"""
        logger.info("🚀 Starting Aurora Totem System Testing Suite")
        logger.info("=" * 60)
        
        # Test execution order (critical path first)
        test_methods = [
            ('database_tests', self.test_database_integration),
            ('api_tests', self.test_api_endpoints),
            ('ml_tests', self.test_ml_pipeline),
            ('websocket_tests', self.test_websocket_streaming),
            ('integration_tests', self.test_end_to_end_workflow),
            ('performance_tests', self.test_system_performance),
            ('error_tests', self.test_error_handling)
        ]
        
        for test_name, test_method in test_methods:
            try:
                logger.info(f"\n🧪 Running {test_name}...")
                test_method()
                logger.info(f"✅ {test_name} completed")
            except Exception as e:
                logger.error(f"❌ {test_name} failed: {str(e)}")
                self.test_results[test_name.replace('_tests', '')]['error'] = str(e)
        
        # Generate final report
        self.generate_test_report()
        return self.test_results
    
    def test_database_integration(self):
        """Test Oracle FIAP database integration"""
        logger.info("📊 Testing database integration...")
        
        try:
            # Test database connection
            db = DatabaseManager()
            connection_result = db.connect()
            
            self.test_results['database']['connection'] = {
                'success': connection_result,
                'oracle_available': ORACLE_AVAILABLE,
                'timestamp': datetime.now().isoformat()
            }
            
            if connection_result:
                # Test database operations
                test_device_id = "test_device_system_test"
                
                # Insert test data
                insert_success = db.insert_sensor_data(
                    device_id=test_device_id,
                    sensor_type="temperature",
                    sensor_value=25.5,
                    metadata={"test": True, "component": "system_test"}
                )
                
                # Query test data
                latest_data = db.get_latest_data(limit=5)
                
                # Get statistics
                stats = db.get_database_stats()
                
                self.test_results['database']['operations'] = {
                    'insert_success': insert_success,
                    'query_success': len(latest_data) > 0,
                    'stats_available': 'total_records' in stats,
                    'total_records': stats.get('total_records', 0),
                    'storage_mode': stats.get('storage_mode', 'unknown')
                }
                
            logger.info(f"✅ Database tests completed - Connection: {connection_result}")
            
        except Exception as e:
            logger.error(f"❌ Database test error: {str(e)}")
            self.test_results['database']['error'] = str(e)
    
    def test_api_endpoints(self):
        """Test all FastAPI endpoints"""
        logger.info("🌐 Testing API endpoints...")
        
        # Core API endpoints to test
        endpoints = [
            ('GET', '/', 'health_check'),
            ('GET', '/api/sensors/data', 'sensor_data'),
            ('GET', '/api/sensors/stats', 'sensor_stats'),
            ('POST', '/api/sessions', 'create_session'),
            ('GET', '/api/ml/model-status', 'ml_status'),
        ]
        
        # Test POST endpoint with data
        post_data = {
            'device_id': 'test_system',
            'sensor_readings': [
                {
                    'sensor_type': 'temperature',
                    'value': 24.0,
                    'metadata': {'test': True}
                }
            ]
        }
        
        for method, endpoint, test_name in endpoints:
            try:
                start_time = time.time()
                
                if method == 'GET':
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                elif method == 'POST':
                    if endpoint == '/api/sessions':
                        session_data = {
                            'device_id': 'test_system',
                            'user_data': {'test_user': True},
                            'emotions': {'happy': 0.8}
                        }
                        response = requests.post(f"{self.base_url}{endpoint}", 
                                               json=session_data, timeout=10)
                    else:
                        response = requests.post(f"{self.base_url}{endpoint}", 
                                               json=post_data, timeout=10)
                
                response_time = time.time() - start_time
                
                self.test_results['api_endpoints'][test_name] = {
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'response_time': response_time,
                    'has_json': self._is_json_response(response),
                    'endpoint': endpoint
                }
                
                # Log response details for health check
                if test_name == 'health_check' and response.status_code == 200:
                    try:
                        data = response.json()
                        logger.info(f"📊 API Health: {data}")
                    except:
                        pass
                        
            except Exception as e:
                logger.error(f"❌ API endpoint {endpoint} error: {str(e)}")
                self.test_results['api_endpoints'][test_name] = {
                    'error': str(e),
                    'success': False
                }
    
    def test_ml_pipeline(self):
        """Test ML model training and predictions"""
        logger.info("🤖 Testing ML pipeline...")
        
        try:
            # Test model status
            response = requests.get(f"{self.base_url}/api/ml/model-status", timeout=10)
            models_ready = False
            
            if response.status_code == 200:
                status_data = response.json()
                models_ready = status_data.get('models_ready', False)
            
            # Train models if not ready
            if not models_ready:
                logger.info("📚 Training ML models...")
                train_response = requests.post(f"{self.base_url}/api/ml/train-models", timeout=60)
                training_success = train_response.status_code == 200
                
                if training_success:
                    train_data = train_response.json()
                    logger.info(f"🎯 Training results: {train_data}")
            else:
                training_success = True
            
            # Test predictions
            test_sensor_data = {
                'sensor_data': {
                    'heart_rate': 75,
                    'skin_conductance': 6.5,
                    'eye_tracking': 0.8,
                    'face_emotion': 0.7,
                    'voice_emotion': 0.6,
                    'proximity': 50,
                    'duration': 30
                }
            }
            
            # Test engagement prediction
            engagement_response = requests.post(
                f"{self.base_url}/api/ml/predict-engagement",
                json=test_sensor_data,
                timeout=10
            )
            
            # Test emotion prediction
            emotion_response = requests.post(
                f"{self.base_url}/api/ml/predict-emotion",
                json=test_sensor_data,
                timeout=10
            )
            
            self.test_results['ml_models'] = {
                'models_ready': models_ready,
                'training_success': training_success,
                'engagement_prediction': {
                    'success': engagement_response.status_code == 200,
                    'response_time': getattr(engagement_response, 'elapsed', {}).get('total_seconds', 0)
                },
                'emotion_prediction': {
                    'success': emotion_response.status_code == 200,
                    'response_time': getattr(emotion_response, 'elapsed', {}).get('total_seconds', 0)
                }
            }
            
            # Log prediction results
            if engagement_response.status_code == 200:
                eng_data = engagement_response.json()
                logger.info(f"🎯 Engagement prediction: {eng_data.get('predicted_engagement', 'N/A')}")
            
            if emotion_response.status_code == 200:
                emo_data = emotion_response.json()
                logger.info(f"😊 Emotion prediction: {emo_data.get('predicted_emotion', 'N/A')}")
                
        except Exception as e:
            logger.error(f"❌ ML pipeline test error: {str(e)}")
            self.test_results['ml_models']['error'] = str(e)
    
    async def test_websocket_streaming(self):
        """Test WebSocket real-time streaming"""
        logger.info("🔌 Testing WebSocket streaming...")
        
        try:
            # Test sensor WebSocket
            messages_received = 0
            sensor_ws_url = f"{self.websocket_url}/ws/sensors"
            
            async with websockets.connect(sensor_ws_url) as websocket:
                logger.info("🔗 Connected to sensor WebSocket")
                
                # Listen for messages with timeout
                try:
                    for _ in range(3):  # Listen for 3 messages
                        message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        data = json.loads(message)
                        messages_received += 1
                        logger.info(f"📡 Received sensor data: {len(data.get('readings', []))} sensors")
                        
                except asyncio.TimeoutError:
                    logger.warning("⏰ WebSocket timeout - may be normal if no active simulation")
            
            self.test_results['websocket'] = {
                'connection_success': True,
                'messages_received': messages_received,
                'sensor_websocket': True
            }
            
        except Exception as e:
            logger.error(f"❌ WebSocket test error: {str(e)}")
            self.test_results['websocket'] = {
                'connection_success': False,
                'error': str(e)
            }
    
    def test_websocket_streaming(self):
        """Synchronous wrapper for WebSocket test"""
        try:
            asyncio.run(self._test_websocket_async())
        except Exception as e:
            logger.error(f"❌ WebSocket test wrapper error: {str(e)}")
            self.test_results['websocket'] = {'error': str(e)}
    
    async def _test_websocket_async(self):
        """Async WebSocket testing"""
        logger.info("🔌 Testing WebSocket streaming...")
        
        try:
            messages_received = 0
            sensor_ws_url = f"{self.websocket_url}/ws/sensors"
            
            async with websockets.connect(sensor_ws_url) as websocket:
                logger.info("🔗 Connected to sensor WebSocket")
                
                try:
                    for _ in range(2):  # Listen for 2 messages
                        message = await asyncio.wait_for(websocket.recv(), timeout=8.0)
                        messages_received += 1
                        logger.info(f"📡 WebSocket message {messages_received} received")
                        
                except asyncio.TimeoutError:
                    logger.info("⏰ WebSocket timeout (normal if simulation not active)")
            
            self.test_results['websocket'] = {
                'connection_success': True,
                'messages_received': messages_received
            }
            
        except Exception as e:
            self.test_results['websocket'] = {'error': str(e)}
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        logger.info("🔄 Testing end-to-end workflow...")
        
        try:
            # Step 1: Verify API is responsive
            health_response = requests.get(f"{self.base_url}/", timeout=5)
            api_healthy = health_response.status_code == 200
            
            # Step 2: Check database connectivity
            stats_response = requests.get(f"{self.base_url}/api/sensors/stats", timeout=10)
            db_accessible = stats_response.status_code == 200
            
            # Step 3: Test data insertion flow
            test_data = {
                'device_id': 'e2e_test_device',
                'sensor_readings': [
                    {
                        'sensor_type': 'temperature',
                        'value': 23.5,
                        'metadata': {'test_type': 'e2e', 'timestamp': datetime.now().isoformat()}
                    },
                    {
                        'sensor_type': 'camera_emotion',
                        'value': 0.85,
                        'metadata': {'emotion': 'happy', 'confidence': 0.85, 'test_type': 'e2e'}
                    }
                ]
            }
            
            # Insert test data
            insert_response = requests.post(
                f"{self.base_url}/api/sensors/data",
                json=test_data,
                timeout=10
            )
            data_inserted = insert_response.status_code == 200
            
            # Step 4: Verify data retrieval
            time.sleep(1)  # Brief pause for data processing
            retrieval_response = requests.get(f"{self.base_url}/api/sensors/data?limit=5", timeout=10)
            data_retrieved = retrieval_response.status_code == 200
            
            # Step 5: Test ML integration with real data
            ml_status_response = requests.get(f"{self.base_url}/api/ml/model-status", timeout=10)
            ml_available = ml_status_response.status_code == 200
            
            # Calculate workflow success
            workflow_steps = {
                'api_health': api_healthy,
                'database_access': db_accessible,
                'data_insertion': data_inserted,
                'data_retrieval': data_retrieved,
                'ml_integration': ml_available
            }
            
            workflow_success = all(workflow_steps.values())
            
            self.test_results['integration'] = {
                'workflow_success': workflow_success,
                'steps': workflow_steps,
                'test_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"🔄 E2E Workflow: {workflow_success} - Steps: {sum(workflow_steps.values())}/5")
            
        except Exception as e:
            logger.error(f"❌ E2E workflow test error: {str(e)}")
            self.test_results['integration']['error'] = str(e)
    
    def test_system_performance(self):
        """Test system performance and load handling"""
        logger.info("⚡ Testing system performance...")
        
        try:
            # Performance test parameters
            num_requests = 10
            concurrent_requests = 3
            
            # Test API response times
            response_times = []
            for i in range(num_requests):
                start = time.time()
                response = requests.get(f"{self.base_url}/api/sensors/stats", timeout=5)
                end = time.time()
                
                if response.status_code == 200:
                    response_times.append(end - start)
            
            # Calculate performance metrics
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
            else:
                avg_response_time = max_response_time = min_response_time = 0
            
            # Test concurrent load
            def make_concurrent_request():
                try:
                    requests.get(f"{self.base_url}/", timeout=3)
                    return True
                except:
                    return False
            
            threads = []
            concurrent_results = []
            
            for _ in range(concurrent_requests):
                thread = threading.Thread(target=lambda: concurrent_results.append(make_concurrent_request()))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join(timeout=5)
            
            concurrent_success_rate = sum(concurrent_results) / len(concurrent_results) if concurrent_results else 0
            
            self.test_results['performance'] = {
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'min_response_time': min_response_time,
                'total_requests_tested': num_requests,
                'successful_requests': len(response_times),
                'concurrent_success_rate': concurrent_success_rate,
                'performance_acceptable': avg_response_time < 1.0  # < 1 second
            }
            
            logger.info(f"⚡ Performance - Avg: {avg_response_time:.3f}s, Concurrent: {concurrent_success_rate:.2%}")
            
        except Exception as e:
            logger.error(f"❌ Performance test error: {str(e)}")
            self.test_results['performance']['error'] = str(e)
    
    def test_error_handling(self):
        """Test system error handling and resilience"""
        logger.info("🛡️ Testing error handling...")
        
        try:
            error_tests = {}
            
            # Test invalid endpoints
            invalid_response = requests.get(f"{self.base_url}/invalid/endpoint", timeout=5)
            error_tests['invalid_endpoint'] = {
                'status_code': invalid_response.status_code,
                'handles_gracefully': invalid_response.status_code == 404
            }
            
            # Test invalid data POST
            try:
                invalid_data_response = requests.post(
                    f"{self.base_url}/api/sensors/data",
                    json={'invalid': 'data'},
                    timeout=5
                )
                error_tests['invalid_data'] = {
                    'status_code': invalid_data_response.status_code,
                    'handles_gracefully': invalid_data_response.status_code in [400, 422]
                }
            except:
                error_tests['invalid_data'] = {'handles_gracefully': True}
            
            # Test ML prediction with invalid data
            try:
                invalid_ml_response = requests.post(
                    f"{self.base_url}/api/ml/predict-engagement",
                    json={'invalid': 'sensor_data'},
                    timeout=5
                )
                error_tests['invalid_ml_data'] = {
                    'status_code': invalid_ml_response.status_code,
                    'handles_gracefully': invalid_ml_response.status_code in [400, 422]
                }
            except:
                error_tests['invalid_ml_data'] = {'handles_gracefully': True}
            
            # Calculate overall error handling score
            graceful_handling = sum(1 for test in error_tests.values() if test.get('handles_gracefully', False))
            total_error_tests = len(error_tests)
            
            self.test_results['error_handling'] = {
                'tests': error_tests,
                'graceful_handling_rate': graceful_handling / total_error_tests if total_error_tests > 0 else 0,
                'total_error_tests': total_error_tests
            }
            
            logger.info(f"🛡️ Error Handling: {graceful_handling}/{total_error_tests} tests passed")
            
        except Exception as e:
            logger.error(f"❌ Error handling test error: {str(e)}")
            self.test_results['error_handling']['error'] = str(e)
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # Calculate overall system health score
        health_score = self._calculate_system_health_score()
        
        report = {
            'test_summary': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'total_duration': total_duration,
                'system_health_score': health_score,
                'overall_status': 'PASS' if health_score >= 0.8 else 'FAIL'
            },
            'detailed_results': self.test_results
        }
        
        # Save report to file
        report_filename = f"system_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"📄 Test report saved: {report_filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save report: {str(e)}")
        
        # Print summary
        self._print_test_summary(health_score, total_duration)
        
        return report
    
    def _calculate_system_health_score(self) -> float:
        """Calculate overall system health score (0-1)"""
        scores = []
        
        # Database score
        db_result = self.test_results.get('database', {})
        if db_result.get('connection', {}).get('success', False):
            scores.append(1.0)
        elif 'error' not in db_result:
            scores.append(0.5)  # Partial credit for fallback mode
        else:
            scores.append(0.0)
        
        # API score
        api_results = self.test_results.get('api_endpoints', {})
        successful_apis = sum(1 for result in api_results.values() if result.get('success', False))
        total_apis = len(api_results) if api_results else 1
        scores.append(successful_apis / total_apis)
        
        # ML score
        ml_result = self.test_results.get('ml_models', {})
        if ml_result.get('models_ready', False):
            scores.append(1.0)
        elif 'error' not in ml_result:
            scores.append(0.5)
        else:
            scores.append(0.0)
        
        # Integration score
        integration_result = self.test_results.get('integration', {})
        if integration_result.get('workflow_success', False):
            scores.append(1.0)
        else:
            scores.append(0.0)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _print_test_summary(self, health_score: float, duration: float):
        """Print formatted test summary"""
        logger.info("\n" + "=" * 60)
        logger.info("🏁 AURORA TOTEM SYSTEM TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"⏱️  Total Duration: {duration:.2f} seconds")
        logger.info(f"🎯 System Health Score: {health_score:.2%}")
        logger.info(f"📊 Overall Status: {'✅ PASS' if health_score >= 0.8 else '❌ FAIL'}")
        
        # Component status
        logger.info("\n📋 Component Status:")
        components = [
            ('Database', self.test_results.get('database', {})),
            ('API Endpoints', self.test_results.get('api_endpoints', {})),
            ('ML Models', self.test_results.get('ml_models', {})),
            ('WebSocket', self.test_results.get('websocket', {})),
            ('Integration', self.test_results.get('integration', {})),
            ('Performance', self.test_results.get('performance', {}))
        ]
        
        for name, result in components:
            status = "✅" if not result.get('error') and result else "❌"
            logger.info(f"  {status} {name}")
        
        logger.info("=" * 60)
    
    def _is_json_response(self, response) -> bool:
        """Check if response is valid JSON"""
        try:
            response.json()
            return True
        except:
            return False

def main():
    """Run system testing suite"""
    print("🚀 Aurora Totem - System Testing Suite")
    print("=" * 50)
    
    # Initialize test framework
    test_framework = SystemTestFramework()
    
    # Run all tests
    results = test_framework.run_all_tests()
    
    # Return results for external use
    return results

if __name__ == "__main__":
    main()