#!/usr/bin/env python3
"""
Test client for Azure Function on IoT Edge
Tests all endpoints with various scenarios
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
EDGE_DEVICE_URL = "http://localhost:8000"
TIMEOUT = 5


class EdgeFunctionTester:
    """Test Azure Function running on IoT Edge"""
    
    def __init__(self, base_url=EDGE_DEVICE_URL):
        self.base_url = base_url
        self.results = []
    
    def test_health(self):
        """Test health check endpoint"""
        
        print("\n🏥 Testing Health Check...")
        print("-" * 70)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=TIMEOUT)
            data = response.json()
            
            if response.status_code == 200 and data.get('status') == 'healthy':
                print("✅ Health check PASSED")
                print(f"   Status: {data['status']}")
                print(f"   Uptime: {data.get('uptime', 'N/A')}")
                print(f"   Messages processed: {data.get('messages_processed', 0)}")
                self.results.append(('Health Check', True))
                return True
            else:
                print("❌ Health check FAILED")
                print(f"   Status: {data}")
                self.results.append(('Health Check', False))
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.results.append(('Health Check', False))
            return False
    
    def test_classify(self):
        """Test fruit classification endpoint"""
        
        print("\n🍎 Testing Fruit Classification...")
        print("-" * 70)
        
        # Sample base64 image (1x1 transparent PNG)
        test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        test_cases = [
            {
                'name': 'Apple (Ripe)',
                'fruit_type': 'apple',
                'image_data': test_image,
                'device_id': 'camera-01'
            },
            {
                'name': 'Banana (Unripe)',
                'fruit_type': 'banana',
                'image_data': test_image,
                'device_id': 'camera-02'
            },
            {
                'name': 'Tomato (Ripe)',
                'fruit_type': 'tomato',
                'image_data': test_image,
                'device_id': 'camera-03'
            },
        ]
        
        passed = 0
        
        for test in test_cases:
            try:
                payload = {
                    'image_data': test['image_data'],
                    'fruit_type': test['fruit_type'],
                    'device_id': test['device_id']
                }
                
                response = requests.post(
                    f"{self.base_url}/classify",
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=TIMEOUT
                )
                
                data = response.json()
                
                if response.status_code == 200 and data.get('success'):
                    print(f"✅ {test['name']}")
                    print(f"   Prediction: {data.get('prediction')}")
                    print(f"   Confidence: {data.get('confidence', 0)*100:.1f}%")
                    print(f"   Location: {data.get('location')}")
                    passed += 1
                else:
                    print(f"❌ {test['name']}")
                    print(f"   Error: {data.get('error', 'Unknown')}")
                    
            except Exception as e:
                print(f"❌ {test['name']}: {str(e)}")
        
        all_passed = passed == len(test_cases)
        self.results.append(('Classification', all_passed))
        return all_passed
    
    def test_iot_events(self):
        """Test IoT event processing endpoint"""
        
        print("\n📡 Testing IoT Event Processing...")
        print("-" * 70)
        
        test_cases = [
            {
                'name': 'Temperature Sensor',
                'device_id': 'sensor-temp-01',
                'sensor_data': {'temperature': 22.5, 'humidity': 65}
            },
            {
                'name': 'Ripeness Sensor',
                'device_id': 'sensor-ripeness-01',
                'sensor_data': {'ripeness': 'ripe', 'confidence': 0.92}
            },
            {
                'name': 'Multi-sensor',
                'device_id': 'sensor-multi-01',
                'sensor_data': {
                    'temperature': 25.0,
                    'humidity': 70,
                    'ripeness': 'unripe'
                }
            },
        ]
        
        passed = 0
        
        for test in test_cases:
            try:
                payload = {
                    'device_id': test['device_id'],
                    'sensor_data': test['sensor_data'],
                    'timestamp': datetime.now().isoformat() + 'Z'
                }
                
                response = requests.post(
                    f"{self.base_url}/process-iot-event",
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=TIMEOUT
                )
                
                data = response.json()
                
                if response.status_code == 200 and data.get('success'):
                    print(f"✅ {test['name']}")
                    print(f"   Device: {test['device_id']}")
                    print(f"   Status: {data.get('message')}")
                    passed += 1
                else:
                    print(f"❌ {test['name']}")
                    print(f"   Error: {data.get('error', 'Unknown')}")
                    
            except Exception as e:
                print(f"❌ {test['name']}: {str(e)}")
        
        all_passed = passed == len(test_cases)
        self.results.append(('IoT Events', all_passed))
        return all_passed
    
    def test_storage(self):
        """Test local blob storage endpoint"""
        
        print("\n💾 Testing Local Storage...")
        print("-" * 70)
        
        try:
            payload = {
                'filename': f'test_data_{int(time.time())}.json',
                'data': {
                    'device_id': 'test-device',
                    'timestamp': datetime.now().isoformat(),
                    'sensor_readings': {
                        'temperature': 22.5,
                        'humidity': 65,
                        'ripeness': 'ripe'
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/store-blob",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=TIMEOUT
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                print(f"✅ Data Storage")
                print(f"   Filename: {payload['filename']}")
                print(f"   Path: {data.get('filepath')}")
                self.results.append(('Storage', True))
                return True
            else:
                print(f"❌ Data Storage Failed")
                print(f"   Error: {data.get('error', 'Unknown')}")
                self.results.append(('Storage', False))
                return False
                
        except Exception as e:
            print(f"❌ Storage test error: {str(e)}")
            self.results.append(('Storage', False))
            return False
    
    def test_statistics(self):
        """Test statistics endpoint"""
        
        print("\n📊 Testing Statistics...")
        print("-" * 70)
        
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=TIMEOUT)
            data = response.json()
            
            if response.status_code == 200:
                stats = data.get('statistics', {})
                print(f"✅ Statistics Retrieved")
                print(f"   Total requests: {stats.get('total_requests', 0)}")
                print(f"   Successful: {stats.get('successful_processing', 0)}")
                print(f"   Errors: {stats.get('errors', 0)}")
                print(f"   Messages processed: {stats.get('messages_processed', 0)}")
                self.results.append(('Statistics', True))
                return True
            else:
                print(f"❌ Statistics retrieval failed")
                self.results.append(('Statistics', False))
                return False
                
        except Exception as e:
            print(f"❌ Statistics error: {str(e)}")
            self.results.append(('Statistics', False))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        
        print("\n" + "="*70)
        print("🧪 AZURE FUNCTION ON IoT EDGE - TEST SUITE")
        print("="*70)
        
        # Check connectivity
        try:
            requests.get(f"{self.base_url}/health", timeout=2)
        except Exception as e:
            print(f"\n❌ Cannot connect to {self.base_url}")
            print(f"   Error: {str(e)}")
            print(f"   Make sure the container is running:")
            print(f"   docker run -d -p 8000:8000 fruitclassifier:latest")
            sys.exit(1)
        
        # Run tests
        self.test_health()
        self.test_classify()
        self.test_iot_events()
        self.test_storage()
        self.test_statistics()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        
        print("\n" + "="*70)
        print("📋 TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for _, result in self.results if result)
        total = len(self.results)
        
        for test_name, result in self.results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed! Container is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Check logs for details.")
        
        return passed == total


def main():
    """Main test runner"""
    
    tester = EdgeFunctionTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
