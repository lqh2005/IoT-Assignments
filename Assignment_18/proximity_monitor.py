"""
Proximity Monitor Module
Simulates and controls HC-SR04 ultrasonic distance sensor for object detection.
"""

import time
import logging
import random
from typing import Tuple

logger = logging.getLogger(__name__)


class ProximityMonitor:
    """
    HC-SR04 Ultrasonic Distance Sensor abstraction.
    Supports both real GPIO and simulator modes.
    
    Distance calculation:
    - Speed of sound: 343 m/s (20°C)
    - Round trip distance: sound_speed * pulse_time / 2
    """
    
    def __init__(self, trigger_distance=20, simulator_mode=True):
        """
        Initialize proximity monitor.
        
        Args:
            trigger_distance: Distance threshold in cm to trigger detection
            simulator_mode: If True, simulate sensor; if False, use real GPIO
        """
        self.trigger_distance = trigger_distance
        self.simulator_mode = simulator_mode
        self.last_distance = None
        self.measurements_count = 0
        
        if not simulator_mode:
            self._init_gpio()
        else:
            logger.info(f"ProximityMonitor initialized in SIMULATOR mode")
            logger.info(f"Trigger distance set to {trigger_distance}cm")
    
    def _init_gpio(self):
        """Initialize GPIO pins for real HC-SR04 sensor."""
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            
            # HC-SR04 pins
            self.TRIG_PIN = 23  # GPIO 23
            self.ECHO_PIN = 24  # GPIO 24
            
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.TRIG_PIN, GPIO.OUT)
            GPIO.setup(self.ECHO_PIN, GPIO.IN)
            GPIO.output(self.TRIG_PIN, GPIO.LOW)
            
            logger.info("GPIO initialized for HC-SR04 sensor")
        
        except ImportError:
            logger.error("RPi.GPIO not available - falling back to simulator")
            self.simulator_mode = True
    
    def measure(self) -> Tuple[float, bool]:
        """
        Measure distance to object.
        
        Returns:
            Tuple[distance_cm, object_detected]
            - distance_cm: Distance in centimeters
            - object_detected: Boolean indicating if object is within trigger distance
        """
        if self.simulator_mode:
            distance = self._simulate_measurement()
        else:
            distance = self._read_real_sensor()
        
        self.last_distance = distance
        self.measurements_count += 1
        
        # Detect if object is close enough
        object_detected = distance < self.trigger_distance and distance > 0
        
        return distance, object_detected
    
    def _simulate_measurement(self) -> float:
        """Simulate distance measurement with realistic variation."""
        # Simulate two scenarios:
        # 1. No object (distance 100-150cm)
        # 2. Object approaching (distance 10-25cm)
        
        if random.random() < 0.1:  # 10% chance of detecting object
            # Object detected - simulate getting closer
            distance = random.uniform(15, 25)
        else:
            # No object - far away
            distance = random.uniform(100, 150)
        
        # Add measurement noise (±1mm)
        noise = random.uniform(-0.1, 0.1)
        distance = max(0, distance + noise)
        
        logger.debug(f"Simulated distance: {distance:.2f}cm")
        return distance
    
    def _read_real_sensor(self) -> float:
        """Read distance from real HC-SR04 sensor."""
        try:
            # Send trigger pulse (10μs)
            self.GPIO.output(self.TRIG_PIN, self.GPIO.HIGH)
            time.sleep(0.00001)
            self.GPIO.output(self.TRIG_PIN, self.GPIO.LOW)
            
            # Wait for echo
            timeout = time.time() + 1.0  # 1 second timeout
            while self.GPIO.input(self.ECHO_PIN) == 0 and time.time() < timeout:
                pulse_start = time.time()
            
            while self.GPIO.input(self.ECHO_PIN) == 1 and time.time() < timeout:
                pulse_end = time.time()
            
            if time.time() >= timeout:
                logger.warning("HC-SR04 sensor timeout")
                return -1
            
            pulse_duration = pulse_end - pulse_start
            
            # Distance = (speed_of_sound * time) / 2
            # 34300 cm/s is speed of sound at 20°C
            distance = (pulse_duration * 34300) / 2
            
            logger.debug(f"Real sensor distance: {distance:.2f}cm")
            return distance
        
        except Exception as e:
            logger.error(f"Sensor reading error: {e}")
            return -1
    
    def get_statistics(self) -> dict:
        """Get sensor statistics."""
        return {
            'measurements': self.measurements_count,
            'last_distance': self.last_distance,
            'trigger_distance': self.trigger_distance,
            'simulator_mode': self.simulator_mode
        }
    
    def cleanup(self):
        """Clean up GPIO resources."""
        if not self.simulator_mode:
            try:
                self.GPIO.cleanup()
                logger.info("GPIO cleanup complete")
            except Exception as e:
                logger.error(f"GPIO cleanup error: {e}")
