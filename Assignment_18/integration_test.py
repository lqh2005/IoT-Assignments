"""
Integration Test Suite for Assignment 18
Tests all components working together as a complete system.
"""

import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrationTester:
    """Complete system integration tests."""
    
    def __init__(self):
        """Initialize test environment."""
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def run_all_tests(self):
        """Run all integration tests."""
        logger.info("="*60)
        logger.info("ASSIGNMENT 18 INTEGRATION TEST SUITE")
        logger.info("="*60)
        
        self.test_proximity_monitor()
        self.test_camera_trigger()
        self.test_cloud_storage()
        self.test_actuator_control()
        self.test_iot_hub_sender()
        self.test_detector_system()
        
        self.print_summary()
    
    def test_proximity_monitor(self):
        """Test proximity sensor component."""
        logger.info("\n--- Testing Proximity Monitor ---")
        
        try:
            from proximity_monitor import ProximityMonitor
            
            # Initialize in simulator mode
            monitor = ProximityMonitor(trigger_distance=20, simulator_mode=True)
            
            # Test measurements
            distances = []
            detections = 0
            
            for i in range(10):
                distance, detected = monitor.measure()
                distances.append(distance)
                if detected:
                    detections += 1
                time.sleep(0.1)
            
            # Verify measurements
            assert all(d >= 0 for d in distances), "Distances should be positive"
            assert len(distances) == 10, "Should have 10 measurements"
            
            stats = monitor.get_statistics()
            assert stats['measurements'] == 10, "Measurement count mismatch"
            
            monitor.cleanup()
            
            self._test_passed("Proximity Monitor", f"Detected {detections}/10 objects")
        
        except Exception as e:
            self._test_failed("Proximity Monitor", str(e))
    
    def test_camera_trigger(self):
        """Test camera capture component."""
        logger.info("\n--- Testing Camera Trigger ---")
        
        try:
            from camera_trigger import CameraTrigger
            
            camera = CameraTrigger(simulator_mode=True, output_dir='./test_captures')
            
            # Capture multiple images
            images = []
            for i in range(3):
                image_path = camera.capture(timestamp=True)
                assert image_path is not None, f"Capture {i} failed"
                assert Path(image_path).exists(), f"Image file not created: {image_path}"
                images.append(image_path)
                time.sleep(0.1)
            
            stats = camera.get_statistics()
            assert stats['captures'] == 3, "Capture count mismatch"
            
            camera.cleanup()
            
            self._test_passed("Camera Trigger", f"Captured {len(images)} images")
        
        except Exception as e:
            self._test_failed("Camera Trigger", str(e))
    
    def test_cloud_storage(self):
        """Test cloud storage component."""
        logger.info("\n--- Testing Cloud Storage ---")
        
        try:
            from cloud_storage import CloudStorageManager
            
            # Create test file
            test_file = Path('./test_upload.txt')
            test_file.write_text("Test content for cloud storage")
            
            storage = CloudStorageManager(
                container_name='test-container',
                simulator_mode=True
            )
            
            # Test upload
            success = storage.upload_blob(str(test_file), 'test_files/test_upload.txt')
            assert success, "Upload failed"
            
            # List blobs
            blobs = storage.list_blobs()
            assert len(blobs) > 0, "No blobs listed"
            
            stats = storage.get_statistics()
            assert stats['uploads'] > 0, "Upload count not tracked"
            
            storage.cleanup()
            test_file.unlink()
            
            self._test_passed("Cloud Storage", f"Uploaded and listed {len(blobs)} blobs")
        
        except Exception as e:
            self._test_failed("Cloud Storage", str(e))
    
    def test_actuator_control(self):
        """Test actuator control component."""
        logger.info("\n--- Testing Actuator Control ---")
        
        try:
            # Add parent directory to path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            from Assignment_16.actuator_control import ActuatorController
            
            actuator = ActuatorController(simulator_mode=True)
            
            # Test LED control
            actuator.set_led('red')
            actuator.set_led('green')
            actuator.set_led('yellow')
            
            # Test buzzer
            actuator.activate_buzzer(duration=0.5)
            
            # Test relay
            actuator.activate_relay(duration=0.5)
            
            actuator.cleanup()
            
            self._test_passed("Actuator Control", "LED, buzzer, and relay working")
        
        except Exception as e:
            self._test_failed("Actuator Control", str(e))
    
    def test_iot_hub_sender(self):
        """Test IoT Hub integration component."""
        logger.info("\n--- Testing IoT Hub Sender ---")
        
        try:
            # Add parent directory to path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            from Assignment_16.iot_hub_sender import IoTHubSender
            
            sender = IoTHubSender(simulator_mode=True)
            
            # Test message sending
            message = {
                'fruit': 'apple',
                'ripeness': 'ripe',
                'confidence': 0.95
            }
            
            success = sender.send_message(message)
            assert success, "Failed to send message"
            
            sender.cleanup()
            
            self._test_passed("IoT Hub Sender", "Message sent successfully")
        
        except Exception as e:
            self._test_failed("IoT Hub Sender", str(e))
    
    def test_detector_system(self):
        """Test complete detector system."""
        logger.info("\n--- Testing Complete System ---")
        
        try:
            from app import FruitQualityDetector
            
            # Initialize detector
            config = {
                'proximity': {'trigger_distance': 20, 'simulator_mode': True},
                'camera': {'device_id': 0, 'simulator_mode': True},
                'storage': {'connection_string': '', 'container_name': 'fruit-images', 'simulator_mode': True},
                'iot_hub': {'connection_string': '', 'simulator_mode': True},
                'detection_interval': 0.1
            }
            
            detector = FruitQualityDetector(config=config)
            
            # Run for a short time
            import threading
            
            detector.running = True
            
            # Simulate a few detection cycles
            for i in range(5):
                distance, detected = detector.proximity_monitor.measure()
                
                if detected:
                    logger.info(f"Cycle {i}: Object detected at {distance:.1f}cm")
                    # Would trigger capture and classification
                else:
                    logger.info(f"Cycle {i}: No object (distance {distance:.1f}cm)")
                
                time.sleep(0.2)
            
            detector.shutdown()
            
            stats = detector.get_statistics()
            
            self._test_passed("Complete System", 
                            f"System ran for {stats['uptime_seconds']:.1f}s, "
                            f"{stats['detections']} detections")
        
        except Exception as e:
            self._test_failed("Complete System", str(e))
    
    def _test_passed(self, test_name, details=""):
        """Record passed test."""
        self.tests_passed += 1
        message = f"✅ PASS: {test_name}"
        if details:
            message += f" ({details})"
        logger.info(message)
        self.test_results.append((test_name, "PASS", details))
    
    def _test_failed(self, test_name, error):
        """Record failed test."""
        self.tests_failed += 1
        logger.error(f"❌ FAIL: {test_name} - {error}")
        self.test_results.append((test_name, "FAIL", error))
    
    def print_summary(self):
        """Print test summary."""
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        for test_name, status, details in self.test_results:
            symbol = "✅" if status == "PASS" else "❌"
            logger.info(f"{symbol} {test_name}: {status} - {details}")
        
        logger.info("-"*60)
        logger.info(f"Total: {self.tests_passed + self.tests_failed} tests")
        logger.info(f"Passed: {self.tests_passed}")
        logger.info(f"Failed: {self.tests_failed}")
        logger.info("="*60)
        
        # Return exit code
        return 0 if self.tests_failed == 0 else 1


def main():
    """Run integration tests."""
    tester = IntegrationTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
