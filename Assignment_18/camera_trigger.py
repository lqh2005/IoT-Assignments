"""
Camera Trigger Module
Captures images when proximity sensor detects objects.
Supports both real USB camera and simulator modes.
"""

import cv2
import logging
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class CameraTrigger:
    """
    USB Camera control for capturing fruit images.
    Supports real OpenCV camera and simulator mode.
    """
    
    def __init__(self, device_id=0, simulator_mode=True, output_dir='./captures'):
        """
        Initialize camera.
        
        Args:
            device_id: Camera device ID (0 for default camera)
            simulator_mode: If True, generate synthetic images
            output_dir: Directory to save captured images
        """
        self.device_id = device_id
        self.simulator_mode = simulator_mode
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.capture_count = 0
        self.camera = None
        
        if not simulator_mode:
            self._init_camera()
        else:
            logger.info("CameraTrigger initialized in SIMULATOR mode")
    
    def _init_camera(self):
        """Initialize real USB camera."""
        try:
            self.camera = cv2.VideoCapture(self.device_id)
            
            if not self.camera.isOpened():
                logger.error(f"Failed to open camera device {self.device_id}")
                self.simulator_mode = True
                return
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            
            logger.info(f"Camera device {self.device_id} initialized")
        
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            self.simulator_mode = True
    
    def capture(self, timestamp=True) -> str:
        """
        Capture image from camera.
        
        Args:
            timestamp: If True, add timestamp to filename
        
        Returns:
            Path to captured image, or None if capture failed
        """
        try:
            if self.simulator_mode:
                image_path = self._capture_simulated()
            else:
                image_path = self._capture_real()
            
            if image_path:
                self.capture_count += 1
                logger.info(f"Image captured: {image_path}")
                return image_path
            else:
                logger.warning("Failed to capture image")
                return None
        
        except Exception as e:
            logger.error(f"Capture error: {e}")
            return None
    
    def _capture_simulated(self) -> str:
        """Generate synthetic fruit image."""
        try:
            import numpy as np
            
            # Create synthetic image (640x480 RGB)
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Add gradient background
            for i in range(480):
                frame[i, :] = [50 + i//5, 100, 150]
            
            # Draw simulated fruit (circle)
            import random
            fruits = [
                {'name': 'apple', 'color': (0, 0, 255)},      # Red
                {'name': 'banana', 'color': (0, 255, 255)},   # Yellow
                {'name': 'orange', 'color': (0, 165, 255)},   # Orange
                {'name': 'tomato', 'color': (0, 100, 255)}    # Red-orange
            ]
            
            fruit = random.choice(fruits)
            center = (320, 240)
            radius = 80
            
            cv2.circle(frame, center, radius, fruit['color'], -1)
            cv2.circle(frame, center, radius, (255, 255, 255), 2)
            
            # Add ripeness indicator
            ripeness_text = random.choice(['RIPE', 'UNRIPE', 'OVERRIPE'])
            cv2.putText(frame, ripeness_text, (250, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
            
            # Save image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            filename = f"{fruit['name']}_{timestamp}.jpg"
            image_path = self.output_dir / filename
            
            cv2.imwrite(str(image_path), frame)
            logger.debug(f"Synthetic image created: {image_path}")
            
            return str(image_path)
        
        except Exception as e:
            logger.error(f"Synthetic image generation error: {e}")
            return None
    
    def _capture_real(self) -> str:
        """Capture image from real camera."""
        try:
            if not self.camera or not self.camera.isOpened():
                logger.error("Camera not available")
                return None
            
            # Capture multiple frames to allow auto-focus
            for _ in range(5):
                ret, frame = self.camera.read()
            
            if not ret or frame is None:
                logger.error("Failed to read frame from camera")
                return None
            
            # Save frame
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            filename = f"capture_{timestamp}.jpg"
            image_path = self.output_dir / filename
            
            cv2.imwrite(str(image_path), frame)
            logger.debug(f"Real camera image saved: {image_path}")
            
            return str(image_path)
        
        except Exception as e:
            logger.error(f"Real camera capture error: {e}")
            return None
    
    def get_statistics(self) -> dict:
        """Get camera statistics."""
        return {
            'captures': self.capture_count,
            'device_id': self.device_id,
            'simulator_mode': self.simulator_mode,
            'output_dir': str(self.output_dir)
        }
    
    def cleanup(self):
        """Release camera resources."""
        if self.camera and self.camera.isOpened():
            try:
                self.camera.release()
                logger.info("Camera released")
            except Exception as e:
                logger.error(f"Camera cleanup error: {e}")
