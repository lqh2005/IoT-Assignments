"""
Configuration Manager for Assignment 18
Loads settings from .env file and environment variables.
"""

import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration management for the fruit detector system."""
    
    def __init__(self):
        """Initialize configuration from environment."""
        self._load_env()
        self.config = self._build_config()
    
    @staticmethod
    def _load_env():
        """Load .env file if it exists."""
        env_file = Path('.env')
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logger.info(f"Loaded environment from {env_file}")
    
    @staticmethod
    def _get_bool(key: str, default: bool) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', 'yes', '1', 'on')
    
    @staticmethod
    def _get_int(key: str, default: int) -> int:
        """Get integer environment variable."""
        try:
            return int(os.getenv(key, default))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def _get_float(key: str, default: float) -> float:
        """Get float environment variable."""
        try:
            return float(os.getenv(key, default))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def _get_string(key: str, default: str) -> str:
        """Get string environment variable."""
        return os.getenv(key, default)
    
    def _build_config(self) -> Dict[str, Any]:
        """Build configuration dictionary."""
        return {
            # Simulator Mode
            'simulator_mode': self._get_bool('SIMULATOR_MODE', True),
            
            # Proximity Sensor
            'proximity': {
                'trigger_distance': self._get_float('PROXIMITY_TRIGGER_DISTANCE', 20.0),
                'simulator_mode': self._get_bool('SIMULATOR_MODE', True),
                'gpio_trigger': self._get_int('GPIO_PROXIMITY_TRIGGER', 23),
                'gpio_echo': self._get_int('GPIO_PROXIMITY_ECHO', 24),
            },
            
            # Camera
            'camera': {
                'device_id': self._get_int('CAMERA_DEVICE_ID', 0),
                'simulator_mode': self._get_bool('SIMULATOR_MODE', True),
                'width': self._get_int('CAMERA_WIDTH', 640),
                'height': self._get_int('CAMERA_HEIGHT', 480),
                'fps': self._get_int('CAMERA_FPS', 30),
                'output_dir': self._get_string('OUTPUT_DIR', './captures'),
            },
            
            # Cloud Storage
            'storage': {
                'connection_string': self._get_string('STORAGE_CONNECTION_STRING', ''),
                'container_name': self._get_string('STORAGE_CONTAINER', 'fruit-images'),
                'simulator_mode': self._get_bool('SIMULATOR_MODE', True),
                'local_dir': self._get_string('LOCAL_STORAGE_DIR', './cloud_storage'),
            },
            
            # IoT Hub
            'iot_hub': {
                'connection_string': self._get_string('IOT_HUB_CONNECTION_STRING', ''),
                'simulator_mode': self._get_bool('SIMULATOR_MODE', True),
            },
            
            # Detection Loop
            'detection': {
                'interval': self._get_float('DETECTION_INTERVAL', 0.5),
                'batch_size': self._get_int('DETECTION_BATCH_SIZE', 1),
                'timeout': self._get_int('DETECTION_TIMEOUT', 30),
            },
            
            # Logging
            'logging': {
                'level': self._get_string('LOG_LEVEL', 'INFO'),
                'debug_mode': self._get_bool('DEBUG_MODE', False),
            },
            
            # Hardware GPIO
            'hardware': {
                'led_red': self._get_int('GPIO_LED_RED', 27),
                'led_green': self._get_int('GPIO_LED_GREEN', 17),
                'led_yellow': self._get_int('GPIO_LED_YELLOW', 22),
                'buzzer': self._get_int('GPIO_BUZZER', 26),
            },
            
            # Classification
            'classification': {
                'confidence_threshold': self._get_float('CONFIDENCE_THRESHOLD', 0.5),
                'model_path': self._get_string('MODEL_PATH', './models/fruit_classifier.h5'),
            },
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (dot notation)."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_dict(self) -> Dict[str, Any]:
        """Get entire configuration as dictionary."""
        return self.config
    
    def validate(self) -> bool:
        """Validate configuration."""
        errors = []
        
        # Validate proximity trigger distance
        if self.config['proximity']['trigger_distance'] <= 0:
            errors.append("PROXIMITY_TRIGGER_DISTANCE must be > 0")
        
        if self.config['proximity']['trigger_distance'] > 400:
            errors.append("PROXIMITY_TRIGGER_DISTANCE must be <= 400cm")
        
        # Validate detection interval
        if self.config['detection']['interval'] <= 0:
            errors.append("DETECTION_INTERVAL must be > 0")
        
        # Validate Azure credentials if not in simulator mode
        if not self.config['simulator_mode']:
            if not self.config['storage']['connection_string']:
                errors.append("STORAGE_CONNECTION_STRING required when SIMULATOR_MODE=false")
            
            if not self.config['iot_hub']['connection_string']:
                errors.append("IOT_HUB_CONNECTION_STRING required when SIMULATOR_MODE=false")
        
        # Log errors
        if errors:
            logger.error("Configuration validation errors:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("Configuration validation passed")
        return True
    
    def print_summary(self):
        """Print configuration summary."""
        logger.info("=" * 60)
        logger.info("CONFIGURATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Simulator Mode: {self.config['simulator_mode']}")
        logger.info(f"Proximity Trigger Distance: {self.config['proximity']['trigger_distance']}cm")
        logger.info(f"Camera Device ID: {self.config['camera']['device_id']}")
        logger.info(f"Detection Interval: {self.config['detection']['interval']}s")
        logger.info(f"Storage: {self.config['storage']['container_name']}")
        logger.info(f"Log Level: {self.config['logging']['level']}")
        logger.info("=" * 60)


# Global configuration instance
_config = None


def get_config() -> Config:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def load_config() -> Dict[str, Any]:
    """Load and return configuration dictionary."""
    config = get_config()
    return config.get_dict()
