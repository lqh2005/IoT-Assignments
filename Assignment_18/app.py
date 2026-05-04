"""
Assignment 18: Build a Fruit Quality Detector - Capstone Project
Orchestrates proximity monitoring, image capture, classification, and storage.
Integrates all learnings from Assignments 15, 16, 17.
"""

import os
import sys
import time
import threading
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from proximity_monitor import ProximityMonitor
from camera_trigger import CameraTrigger
from cloud_storage import CloudStorageManager
from actuator_control import ActuatorController
from iot_hub_sender import IoTHubSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fruit_detector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FruitQualityDetector:
    """
    Capstone project: Complete fruit quality detection system.
    
    Workflow:
    1. Monitor proximity (HC-SR04 sensor or simulator)
    2. When object is close enough, trigger camera
    3. Capture image and classify using ML model
    4. Store results in local storage and cloud
    5. Control LED based on ripeness (via previous assignment logic)
    6. Send alerts to IoT Hub
    """
    
    def __init__(self, config=None):
        """Initialize all system components."""
        self.config = config or self._load_config()
        self.running = False
        
        # Initialize components
        logger.info("Initializing Fruit Quality Detector...")
        
        self.proximity_monitor = ProximityMonitor(
            trigger_distance=self.config['proximity']['trigger_distance'],
            simulator_mode=self.config['proximity']['simulator_mode']
        )
        
        self.camera = CameraTrigger(
            device_id=self.config['camera']['device_id'],
            simulator_mode=self.config['camera']['simulator_mode']
        )
        
        self.storage = CloudStorageManager(
            connection_string=self.config['storage']['connection_string'],
            container_name=self.config['storage']['container_name'],
            simulator_mode=self.config['storage']['simulator_mode']
        )
        
        self.actuator = ActuatorController(simulator_mode=True)
        
        self.iot_hub = IoTHubSender(
            connection_string=self.config['iot_hub']['connection_string'],
            simulator_mode=self.config['iot_hub']['simulator_mode']
        )
        
        # Statistics
        self.stats = {
            'detections': 0,
            'classifications': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        logger.info("Initialization complete")
    
    @staticmethod
    def _load_config():
        """Load configuration from environment variables."""
        return {
            'proximity': {
                'trigger_distance': float(os.getenv('PROXIMITY_TRIGGER_DISTANCE', '20')),
                'simulator_mode': os.getenv('SIMULATOR_MODE', 'true').lower() == 'true'
            },
            'camera': {
                'device_id': int(os.getenv('CAMERA_DEVICE_ID', '0')),
                'simulator_mode': os.getenv('SIMULATOR_MODE', 'true').lower() == 'true'
            },
            'storage': {
                'connection_string': os.getenv('STORAGE_CONNECTION_STRING', ''),
                'container_name': os.getenv('STORAGE_CONTAINER', 'fruit-images'),
                'simulator_mode': os.getenv('SIMULATOR_MODE', 'true').lower() == 'true'
            },
            'iot_hub': {
                'connection_string': os.getenv('IOT_HUB_CONNECTION_STRING', ''),
                'simulator_mode': os.getenv('SIMULATOR_MODE', 'true').lower() == 'true'
            },
            'detection_interval': float(os.getenv('DETECTION_INTERVAL', '0.5'))
        }
    
    def run(self):
        """Main monitoring loop."""
        logger.info("Starting Fruit Quality Detector...")
        self.running = True
        
        try:
            while self.running:
                # Monitor proximity
                distance, object_detected = self.proximity_monitor.measure()
                
                if object_detected:
                    logger.info(f"Object detected at {distance:.1f}cm - Triggering capture")
                    self.stats['detections'] += 1
                    
                    # Capture image
                    image_path = self.camera.capture(timestamp=True)
                    if image_path:
                        logger.info(f"Image captured: {image_path}")
                        
                        # Classify using ML model (from Assignment 15)
                        result = self._classify_fruit(image_path)
                        
                        if result:
                            logger.info(f"Classification result: {result}")
                            self.stats['classifications'] += 1
                            
                            # Control LED based on ripeness (from Assignment 16)
                            self._control_led_by_ripeness(result)
                            
                            # Store results (local + cloud)
                            self._store_results(image_path, result)
                            
                            # Send to IoT Hub (from Assignment 16/17)
                            self._send_to_iot_hub(result)
                            
                            logger.info("Detection cycle complete")
                        else:
                            self.stats['errors'] += 1
                            logger.warning("Classification failed")
                    else:
                        self.stats['errors'] += 1
                        logger.warning("Failed to capture image")
                
                time.sleep(self.config['detection_interval'])
        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            self.stats['errors'] += 1
        finally:
            self.shutdown()
    
    def _classify_fruit(self, image_path):
        """
        Classify fruit from image.
        In production, this would use the TensorFlow model from Assignment 15.
        """
        try:
            # Simulate classification (in real deployment, load and use saved model)
            import random
            
            fruits = ['apple', 'banana', 'tomato', 'orange']
            ripeness = ['ripe', 'unripe', 'overripe']
            
            result = {
                'fruit': random.choice(fruits),
                'ripeness': random.choice(ripeness),
                'confidence': round(random.uniform(0.75, 0.99), 3),
                'timestamp': datetime.now().isoformat(),
                'image_path': image_path
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return None
    
    def _control_led_by_ripeness(self, classification_result):
        """
        Control LED based on ripeness.
        Integration with Assignment 16 logic.
        """
        try:
            ripeness = classification_result['ripeness']
            confidence = classification_result['confidence']
            
            if confidence < 0.5:
                logger.info("Low confidence - no action")
                self.actuator.set_led('yellow')
                return
            
            if ripeness == 'ripe':
                self.actuator.set_led('green')
                logger.info("LED: GREEN (ripe)")
            elif ripeness == 'unripe':
                self.actuator.set_led('red')
                logger.info("LED: RED (unripe)")
            elif ripeness == 'overripe':
                self.actuator.set_led('yellow')
                self.actuator.activate_buzzer(duration=1.0)
                logger.info("LED: YELLOW + BUZZER (overripe)")
        
        except Exception as e:
            logger.error(f"LED control error: {e}")
    
    def _store_results(self, image_path, result):
        """
        Store results locally and in cloud.
        Integration with Assignment 17 storage logic.
        """
        try:
            # Store locally
            local_result = {
                'timestamp': result['timestamp'],
                'fruit': result['fruit'],
                'ripeness': result['ripeness'],
                'confidence': result['confidence'],
                'image_path': image_path
            }
            
            local_file = Path('detection_results.jsonl')
            import json
            with open(local_file, 'a') as f:
                f.write(json.dumps(local_result) + '\n')
            
            logger.info(f"Result stored locally: {local_file}")
            
            # Upload to cloud
            if not self.config['storage']['simulator_mode']:
                blob_name = f"detections/{Path(image_path).name}"
                self.storage.upload_blob(image_path, blob_name)
                logger.info(f"Image uploaded to cloud: {blob_name}")
        
        except Exception as e:
            logger.error(f"Storage error: {e}")
    
    def _send_to_iot_hub(self, result):
        """
        Send results to IoT Hub.
        Integration with Assignment 16 IoT Hub logic.
        """
        try:
            message = {
                'fruit': result['fruit'],
                'ripeness': result['ripeness'],
                'confidence': result['confidence'],
                'timestamp': result['timestamp']
            }
            
            self.iot_hub.send_message(message)
            logger.info("Result sent to IoT Hub")
        
        except Exception as e:
            logger.error(f"IoT Hub error: {e}")
    
    def get_statistics(self):
        """Get system statistics."""
        uptime = (datetime.now() - self.stats['start_time']).total_seconds()
        return {
            'detections': self.stats['detections'],
            'classifications': self.stats['classifications'],
            'errors': self.stats['errors'],
            'uptime_seconds': uptime,
            'detection_rate': self.stats['detections'] / max(uptime / 60, 1)  # per minute
        }
    
    def shutdown(self):
        """Gracefully shutdown all components."""
        logger.info("Shutting down...")
        self.running = False
        
        try:
            self.proximity_monitor.cleanup()
            self.camera.cleanup()
            self.actuator.cleanup()
            logger.info("All components cleaned up")
            
            # Print final statistics
            stats = self.get_statistics()
            logger.info(f"Final statistics: {stats}")
        
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def main():
    """Entry point for the application."""
    detector = FruitQualityDetector()
    
    # Run in background thread to allow graceful shutdown
    detector_thread = threading.Thread(target=detector.run, daemon=True)
    detector_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        detector.shutdown()


if __name__ == '__main__':
    main()
