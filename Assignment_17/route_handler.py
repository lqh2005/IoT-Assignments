"""
Route handlers for Azure Function on IoT Edge
Processes classification and IoT Hub events
"""

import json
import logging
import base64
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class FruitClassificationHandler:
    """Handle fruit classification requests on edge"""
    
    def __init__(self):
        self.processing_log = []
    
    def process_image(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process image classification request
        In real scenario, would call ML model locally
        
        Args:
            request_data: {image_data, fruit_type, device_id}
            
        Returns:
            Classification result
        """
        
        try:
            image_data = request_data.get('image_data')
            fruit_type = request_data.get('fruit_type', 'unknown')
            device_id = request_data.get('device_id', 'unknown')
            
            if not image_data:
                return {
                    'success': False,
                    'error': 'No image data provided'
                }
            
            # Validate base64 image
            try:
                decoded = base64.b64decode(image_data)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Invalid base64 image: {str(e)}'
                }
            
            # In real scenario: run ML classifier on decoded image
            # For now, simulate classification
            prediction = self._simulate_classification(len(decoded), fruit_type)
            
            result = {
                'success': True,
                'device_id': device_id,
                'fruit_type': fruit_type,
                'prediction': prediction['ripeness'],
                'confidence': prediction['confidence'],
                'processed_at': datetime.now().isoformat(),
                'location': 'edge',  # Important: processed on edge, not cloud
                'message': f'Image classified as {prediction["ripeness"]} on edge device'
            }
            
            # Log processing
            self.processing_log.append(result)
            
            logger.info(f"✅ Classification: {fruit_type} → {prediction['ripeness']} ({prediction['confidence']*100:.1f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _simulate_classification(self, image_size: int, fruit_type: str) -> Dict[str, Any]:
        """
        Simulate ML model classification
        In real scenario: replace with actual TensorFlow/PyTorch model
        """
        
        # Simulate different accuracy based on fruit type
        ripeness_map = {
            'apple': {'ripeness': 'ripe', 'confidence': 0.92},
            'banana': {'ripeness': 'unripe', 'confidence': 0.87},
            'tomato': {'ripeness': 'ripe', 'confidence': 0.95},
            'orange': {'ripeness': 'ripe', 'confidence': 0.89},
            'strawberry': {'ripeness': 'ripe', 'confidence': 0.91},
        }
        
        return ripeness_map.get(
            fruit_type.lower(),
            {'ripeness': 'uncertain', 'confidence': 0.45}
        )


class IoTHubEventHandler:
    """Handle IoT Hub events on edge"""
    
    def __init__(self):
        self.event_log = []
    
    def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process IoT Hub event on edge
        
        Args:
            event_data: Event from IoT Hub
            
        Returns:
            Processing result
        """
        
        try:
            device_id = event_data.get('device_id', 'unknown')
            sensor_data = event_data.get('sensor_data', {})
            timestamp = event_data.get('timestamp', datetime.now().isoformat())
            
            # Process event locally
            processed_event = {
                'device_id': device_id,
                'original_timestamp': timestamp,
                'processed_at': datetime.now().isoformat(),
                'processing_location': 'edge',
                'sensor_data': sensor_data,
                'status': 'processed'
            }
            
            # Add local processing logic
            if sensor_data:
                processed_event['summary'] = self._summarize_sensor_data(sensor_data)
            
            # Log event
            self.event_log.append(processed_event)
            
            logger.info(f"✅ Event processed from {device_id} on edge")
            
            return {
                'success': True,
                'message': 'Event processed on edge device',
                'processed_event': processed_event
            }
            
        except Exception as e:
            logger.error(f"Event processing error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _summarize_sensor_data(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize sensor data"""
        
        summary = {
            'data_points': len(sensor_data),
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract key metrics if available
        if 'temperature' in sensor_data:
            summary['temperature'] = sensor_data['temperature']
        
        if 'humidity' in sensor_data:
            summary['humidity'] = sensor_data['humidity']
        
        if 'ripeness' in sensor_data:
            summary['ripeness'] = sensor_data['ripeness']
        
        return summary


class EdgeStorageHandler:
    """Handle local blob storage on edge device"""
    
    def __init__(self, storage_path: str = 'edge_storage'):
        self.storage_path = storage_path
        import os
        os.makedirs(storage_path, exist_ok=True)
    
    def store_data(self, filename: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store data locally"""
        
        try:
            import os
            filepath = os.path.join(self.storage_path, filename)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Data stored: {filepath}")
            
            return {
                'success': True,
                'filepath': filepath,
                'size': os.path.getsize(filepath)
            }
            
        except Exception as e:
            logger.error(f"Storage error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def retrieve_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored data"""
        
        try:
            import os
            filepath = os.path.join(self.storage_path, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Retrieval error: {str(e)}")
            return None
