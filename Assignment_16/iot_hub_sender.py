"""
IoT Hub Sender Module
Send classification results and actuator responses to Azure IoT Hub
Supports both real Azure IoT Hub and local simulator mode
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, Optional


class IoTHubSender:
    """
    Send data to Azure IoT Hub
    Can work in two modes:
    1. Real mode: Connects to actual Azure IoT Hub
    2. Simulator mode: Logs to file/console
    """
    
    def __init__(self, device_id: str, connection_string: Optional[str] = None, simulate: bool = True):
        """
        Initialize IoT Hub sender
        
        Args:
            device_id: Unique device identifier
            connection_string: Azure IoT Hub connection string (optional)
            simulate: If True, simulate sending; if False, use real Azure
        """
        
        self.device_id = device_id
        self.connection_string = connection_string
        self.simulate = simulate
        self.client = None
        self.message_count = 0
        self.messages = []
        
        # Try to initialize real Azure IoT Hub connection
        if not simulate and connection_string:
            self._init_real_connection()
        else:
            print("✅ IoT Hub Sender initialized (Simulator mode)")
    
    def _init_real_connection(self):
        """Initialize real Azure IoT Hub connection"""
        
        try:
            from azure.iot.device import IoTHubDeviceClient, Message
            
            self.client = IoTHubDeviceClient.create_from_connection_string(
                self.connection_string
            )
            self.client.connect()
            self.simulate = False
            print("✅ Connected to Azure IoT Hub (Real mode)")
            
        except ImportError:
            print("⚠️ azure-iot-device not installed, using simulator mode")
            print("   Install with: pip install azure-iot-device")
            self.simulate = True
        except Exception as e:
            print(f"⚠️ Failed to connect to IoT Hub: {e}")
            print("   Falling back to simulator mode")
            self.simulate = True
    
    def send_message(self, data: Dict[str, Any]) -> bool:
        """
        Send message to IoT Hub
        
        Args:
            data: Dictionary containing classification and actuator data
            
        Returns:
            True if sent successfully, False otherwise
        """
        
        try:
            # Prepare message
            message_body = json.dumps(data, indent=2)
            self.message_count += 1
            
            if self.simulate:
                # Simulator mode: log to console and file
                self._log_message(data)
                print(f"  📨 [SIM] Message #{self.message_count} queued")
                return True
            else:
                # Real mode: send to Azure IoT Hub
                if self.client:
                    from azure.iot.device import Message
                    msg = Message(message_body, content_encoding='utf-8', content_type='application/json')
                    self.client.send_message(msg)
                    self._log_message(data)
                    print(f"  📨 Message #{self.message_count} sent to IoT Hub")
                    return True
                else:
                    print(f"  ❌ No IoT Hub connection")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error sending message: {e}")
            return False
    
    def send_telemetry(self, telemetry_data: Dict[str, Any]) -> bool:
        """
        Send telemetry-only data (lighter weight)
        
        Args:
            telemetry_data: Telemetry metrics
            
        Returns:
            Success status
        """
        
        message = {
            'device_id': self.device_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'telemetry',
            'data': telemetry_data
        }
        
        return self.send_message(message)
    
    def send_alert(self, alert_type: str, message: str, severity: str = 'warning') -> bool:
        """
        Send alert message
        
        Args:
            alert_type: Type of alert (e.g., 'ripeness', 'sensor_error')
            message: Alert message text
            severity: 'critical', 'warning', 'info'
            
        Returns:
            Success status
        """
        
        alert_message = {
            'device_id': self.device_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'alert',
            'alert_type': alert_type,
            'severity': severity,
            'message': message
        }
        
        return self.send_message(alert_message)
    
    def send_batch(self, messages: list) -> int:
        """
        Send multiple messages
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Number of successfully sent messages
        """
        
        sent_count = 0
        for msg in messages:
            if self.send_message(msg):
                sent_count += 1
        
        return sent_count
    
    def _log_message(self, data: Dict[str, Any]):
        """Log message for debugging"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message_id': self.message_count,
            'data': data
        }
        self.messages.append(log_entry)
    
    def get_messages(self, limit: Optional[int] = None) -> list:
        """Get logged messages"""
        
        if limit:
            return self.messages[-limit:]
        return self.messages.copy()
    
    def save_messages(self, filename: str = 'iot_messages.json') -> str:
        """Save all logged messages to file"""
        
        output = {
            'device_id': self.device_id,
            'total_messages': self.message_count,
            'timestamp': datetime.now().isoformat(),
            'messages': self.messages
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✅ Messages saved to {filename}")
        return filename
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get message statistics"""
        
        stats = {
            'total_messages_sent': self.message_count,
            'total_logged_messages': len(self.messages),
            'mode': 'simulator' if self.simulate else 'real',
            'device_id': self.device_id
        }
        
        # Analyze message types
        if self.messages:
            types = {}
            for msg in self.messages:
                msg_type = msg['data'].get('type', 'unknown')
                types[msg_type] = types.get(msg_type, 0) + 1
            stats['message_types'] = types
        
        return stats
    
    def close(self):
        """Close IoT Hub connection"""
        
        if self.client and not self.simulate:
            try:
                self.client.disconnect()
                print("✅ Disconnected from IoT Hub")
            except Exception as e:
                print(f"⚠️ Error disconnecting: {e}")


class IoTHubMessageBuilder:
    """Helper class to build well-formatted IoT Hub messages"""
    
    @staticmethod
    def build_classification_message(device_id: str, fruit_type: str, 
                                    prediction: str, confidence: float,
                                    ripeness: str) -> Dict[str, Any]:
        """Build classification result message"""
        
        return {
            'device_id': device_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'classification',
            'classifier': {
                'fruit_type': fruit_type,
                'prediction': prediction,
                'confidence': float(confidence)
            },
            'classification': {
                'ripeness': ripeness
            }
        }
    
    @staticmethod
    def build_actuator_message(device_id: str, actuator_actions: list) -> Dict[str, Any]:
        """Build actuator action message"""
        
        return {
            'device_id': device_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'actuator_control',
            'actions': actuator_actions
        }
    
    @staticmethod
    def build_decision_message(device_id: str, prediction: str, 
                              decision: str, recommendation: str) -> Dict[str, Any]:
        """Build decision/recommendation message"""
        
        return {
            'device_id': device_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'decision',
            'prediction': prediction,
            'decision': decision,
            'recommendation': recommendation
        }


class IoTHubResponseHandler:
    """Handle responses from IoT Hub (D2C to C2D communication)"""
    
    def __init__(self, client):
        self.client = client
        self.handlers = {}
    
    def receive_message(self):
        """Receive message from IoT Hub (cloud-to-device)"""
        
        if self.client:
            try:
                msg = self.client.receive_message()
                return json.loads(msg.data)
            except Exception as e:
                print(f"Error receiving message: {e}")
                return None
        return None
    
    def register_handler(self, message_type: str, handler_func):
        """Register handler for specific message type"""
        
        self.handlers[message_type] = handler_func
    
    def process_message(self, message: Dict[str, Any]):
        """Process received message with registered handler"""
        
        msg_type = message.get('type', 'unknown')
        if msg_type in self.handlers:
            return self.handlers[msg_type](message)
        return None


def demo():
    """Demonstrate IoT Hub sender"""
    
    print("📤 IoT Hub Sender Demo")
    print("=" * 70)
    
    # Initialize sender (simulator mode)
    sender = IoTHubSender('demo-device-01', simulate=True)
    
    # Test 1: Send classification message
    print("\n1️⃣ Sending Classification Message")
    print("-" * 70)
    msg1 = IoTHubMessageBuilder.build_classification_message(
        device_id='demo-device-01',
        fruit_type='apple',
        prediction='ripe',
        confidence=0.92,
        ripeness='ripe'
    )
    sender.send_message(msg1)
    
    # Test 2: Send actuator message
    print("\n2️⃣ Sending Actuator Message")
    print("-" * 70)
    msg2 = IoTHubMessageBuilder.build_actuator_message(
        device_id='demo-device-01',
        actuator_actions=[
            {'device': 'led_green', 'action': 'ON'},
            {'device': 'buzzer', 'action': 'ON'}
        ]
    )
    sender.send_message(msg2)
    
    # Test 3: Send decision message
    print("\n3️⃣ Sending Decision Message")
    print("-" * 70)
    msg3 = IoTHubMessageBuilder.build_decision_message(
        device_id='demo-device-01',
        prediction='ripe',
        decision='ready_to_harvest',
        recommendation='Pick fruit immediately'
    )
    sender.send_message(msg3)
    
    # Test 4: Send alert
    print("\n4️⃣ Sending Alert Message")
    print("-" * 70)
    sender.send_alert(
        alert_type='ripeness_reached',
        message='Fruit has reached optimal ripeness',
        severity='info'
    )
    
    # Display statistics
    print("\n5️⃣ Statistics")
    print("-" * 70)
    stats = sender.get_statistics()
    print(f"Total messages: {stats['total_messages_sent']}")
    print(f"Mode: {stats['mode']}")
    
    # Save messages
    print("\n6️⃣ Saving Messages")
    print("-" * 70)
    sender.save_messages('demo_iot_messages.json')
    
    # Close
    sender.close()


if __name__ == '__main__':
    demo()
