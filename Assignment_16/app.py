"""
Assignment 16: Respond to Classification Results

Device responds to fruit classifier predictions by:
1. Controlling actuators (LED on/off based on ripeness)
2. Sending data to IoT Hub
3. Implementing decision logic based on predictions
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, Any

# Import actuator and IoT Hub modules
from actuator_control import ActuatorController
from iot_hub_sender import IoTHubSender


class FruitResponseSystem:
    """
    System to respond to fruit classification predictions
    Combines actuator control + IoT Hub messaging
    """
    
    def __init__(self, device_id='fruit-classifier-01'):
        """
        Initialize the response system
        
        Args:
            device_id: Unique identifier for this device
        """
        self.device_id = device_id
        self.actuator = ActuatorController()
        self.iot_hub = IoTHubSender(device_id)
        self.response_log = []
        
        print(f"✅ FruitResponseSystem initialized (Device: {device_id})")
    
    def classify_ripeness(self, prediction: str, confidence: float) -> str:
        """
        Classify ripeness based on ML model prediction
        
        Args:
            prediction: Model output (e.g., "ripe", "unripe", "overripe")
            confidence: Confidence score (0-1)
            
        Returns:
            Ripeness category
        """
        if confidence < 0.5:
            return "uncertain"
        
        ripeness = prediction.lower()
        return ripeness if ripeness in ["ripe", "unripe", "overripe"] else "unknown"
    
    def control_actuator(self, ripeness: str) -> Dict[str, Any]:
        """
        Control actuator based on ripeness classification
        
        Decision Logic:
        - RIPE: Turn on GREEN LED, ready for harvest
        - UNRIPE: Turn on RED LED, not ready yet
        - OVERRIPE: Turn on YELLOW LED + buzzer, spoiling
        
        Args:
            ripeness: Ripeness classification
            
        Returns:
            Actuator response data
        """
        
        response = {
            'timestamp': datetime.now().isoformat(),
            'ripeness': ripeness,
            'actuator_actions': []
        }
        
        if ripeness == "ripe":
            # Green LED: Ready for harvest
            self.actuator.set_led('green', True)
            self.actuator.set_led('red', False)
            self.actuator.set_led('yellow', False)
            self.actuator.buzzer(False)
            
            response['actuator_actions'] = [
                {'device': 'led_green', 'action': 'ON'},
                {'device': 'led_red', 'action': 'OFF'},
                {'device': 'led_yellow', 'action': 'OFF'},
                {'device': 'buzzer', 'action': 'OFF'}
            ]
            response['message'] = "✅ Fruit is RIPE - Ready for harvest!"
            response['recommendation'] = "Pick fruit now"
            
        elif ripeness == "unripe":
            # Red LED: Not ready
            self.actuator.set_led('red', True)
            self.actuator.set_led('green', False)
            self.actuator.set_led('yellow', False)
            self.actuator.buzzer(False)
            
            response['actuator_actions'] = [
                {'device': 'led_green', 'action': 'OFF'},
                {'device': 'led_red', 'action': 'ON'},
                {'device': 'led_yellow', 'action': 'OFF'},
                {'device': 'buzzer', 'action': 'OFF'}
            ]
            response['message'] = "⏳ Fruit is UNRIPE - Wait to harvest"
            response['recommendation'] = "Check again later"
            
        elif ripeness == "overripe":
            # Yellow LED + buzzer: Spoiling
            self.actuator.set_led('yellow', True)
            self.actuator.set_led('red', False)
            self.actuator.set_led('green', False)
            self.actuator.buzzer(True)
            
            response['actuator_actions'] = [
                {'device': 'led_green', 'action': 'OFF'},
                {'device': 'led_red', 'action': 'OFF'},
                {'device': 'led_yellow', 'action': 'ON'},
                {'device': 'buzzer', 'action': 'ON'}
            ]
            response['message'] = "⚠️ Fruit is OVERRIPE - Risk of spoilage!"
            response['recommendation'] = "Pick or discard immediately"
            
        else:
            # Unknown: Turn off all
            self.actuator.set_led('green', False)
            self.actuator.set_led('red', False)
            self.actuator.set_led('yellow', False)
            self.actuator.buzzer(False)
            
            response['actuator_actions'] = [
                {'device': 'all_leds', 'action': 'OFF'},
                {'device': 'buzzer', 'action': 'OFF'}
            ]
            response['message'] = "❓ Ripeness UNKNOWN - Check sensor"
            response['recommendation'] = "Verify classifier output"
        
        return response
    
    def process_prediction(self, prediction: str, confidence: float, 
                          fruit_type: str = "unknown") -> Dict[str, Any]:
        """
        Process classification prediction and respond
        
        Workflow:
        1. Classify ripeness level
        2. Control actuators
        3. Send data to IoT Hub
        4. Log response
        
        Args:
            prediction: Classifier output (ripe/unripe/etc)
            confidence: Confidence score
            fruit_type: Type of fruit (optional)
            
        Returns:
            Complete response with all actions taken
        """
        
        print(f"\n{'='*70}")
        print(f"🍎 Processing Prediction")
        print(f"{'='*70}")
        print(f"  Fruit Type: {fruit_type}")
        print(f"  Prediction: {prediction}")
        print(f"  Confidence: {confidence*100:.1f}%")
        
        # Step 1: Classify ripeness
        ripeness = self.classify_ripeness(prediction, confidence)
        print(f"  Ripeness Classification: {ripeness}")
        
        # Step 2: Control actuator based on ripeness
        print(f"\n  🎛️ Controlling actuators...")
        actuator_response = self.control_actuator(ripeness)
        
        # Display actuator actions
        for action in actuator_response['actuator_actions']:
            print(f"    → {action['device']}: {action['action']}")
        
        print(f"  Message: {actuator_response['message']}")
        
        # Step 3: Prepare IoT Hub payload
        payload = {
            'device_id': self.device_id,
            'timestamp': datetime.now().isoformat(),
            'classifier': {
                'prediction': prediction,
                'confidence': float(confidence),
                'fruit_type': fruit_type
            },
            'classification': {
                'ripeness': ripeness
            },
            'actuator_response': actuator_response,
            'decision': actuator_response['recommendation']
        }
        
        # Step 4: Send to IoT Hub
        print(f"\n  📤 Sending to IoT Hub...")
        try:
            sent = self.iot_hub.send_message(payload)
            if sent:
                print(f"    ✅ Data sent to IoT Hub")
                payload['iot_hub_status'] = 'sent'
            else:
                print(f"    ⚠️ IoT Hub not configured (simulator mode)")
                payload['iot_hub_status'] = 'simulated'
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            payload['iot_hub_status'] = 'failed'
            payload['error'] = str(e)
        
        # Step 5: Log response
        self.response_log.append(payload)
        
        print(f"\n{'='*70}\n")
        
        return payload
    
    def continuous_monitoring(self, test_predictions=None, interval=5):
        """
        Continuous monitoring mode
        Simulates receiving predictions and responding
        
        Args:
            test_predictions: List of test predictions for simulation
            interval: Seconds between checks
        """
        
        # Default test cases if none provided
        if test_predictions is None:
            test_predictions = [
                {'fruit': 'apple', 'prediction': 'ripe', 'confidence': 0.92},
                {'fruit': 'banana', 'prediction': 'unripe', 'confidence': 0.87},
                {'fruit': 'tomato', 'prediction': 'ripe', 'confidence': 0.95},
                {'fruit': 'apple', 'prediction': 'overripe', 'confidence': 0.78},
            ]
        
        print(f"\n🔄 Starting Continuous Monitoring Mode")
        print(f"{'='*70}")
        print(f"Processing {len(test_predictions)} test predictions...")
        print(f"{'='*70}\n")
        
        for i, pred in enumerate(test_predictions, 1):
            print(f"\n[{i}/{len(test_predictions)}] Processing...")
            
            self.process_prediction(
                prediction=pred['prediction'],
                confidence=pred['confidence'],
                fruit_type=pred.get('fruit', 'unknown')
            )
            
            if i < len(test_predictions):
                print(f"Waiting {interval} seconds before next check...")
                time.sleep(interval)
        
        print(f"\n✅ Monitoring session complete!")
        print(f"Total predictions processed: {len(test_predictions)}")
        
        return self.response_log
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get summary statistics of responses"""
        
        if not self.response_log:
            return {'message': 'No responses logged yet'}
        
        ripeness_counts = {}
        for response in self.response_log:
            ripeness = response['classification']['ripeness']
            ripeness_counts[ripeness] = ripeness_counts.get(ripeness, 0) + 1
        
        avg_confidence = sum(
            r['classifier']['confidence'] 
            for r in self.response_log
        ) / len(self.response_log)
        
        stats = {
            'total_predictions': len(self.response_log),
            'ripeness_distribution': ripeness_counts,
            'average_confidence': round(avg_confidence, 3),
            'timestamp': datetime.now().isoformat()
        }
        
        return stats
    
    def save_log(self, filename='response_log.json'):
        """Save response log to file"""
        
        data = {
            'device_id': self.device_id,
            'timestamp': datetime.now().isoformat(),
            'responses': self.response_log,
            'statistics': self.get_statistics()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Response log saved to {filename}")
        return filename
    
    def shutdown(self):
        """Safely shutdown system"""
        
        print(f"\n🛑 Shutting down...")
        
        # Turn off all actuators
        self.actuator.set_led('green', False)
        self.actuator.set_led('red', False)
        self.actuator.set_led('yellow', False)
        self.actuator.buzzer(False)
        
        # Close IoT Hub connection
        self.iot_hub.close()
        
        print(f"✅ System shutdown complete")


def main():
    """Main demonstration"""
    
    print("🍎 Fruit Classifier Response System")
    print("=" * 70)
    print("Demonstrating decision-based response to classification results\n")
    
    # Initialize system
    system = FruitResponseSystem(device_id='fruit-device-01')
    
    # Test scenarios
    print("\n📋 TEST SCENARIOS:")
    print("=" * 70)
    
    test_cases = [
        {
            'name': 'Scenario 1: Ripe Apple',
            'fruit': 'apple',
            'prediction': 'ripe',
            'confidence': 0.92
        },
        {
            'name': 'Scenario 2: Unripe Banana',
            'fruit': 'banana',
            'prediction': 'unripe',
            'confidence': 0.87
        },
        {
            'name': 'Scenario 3: Overripe Tomato',
            'fruit': 'tomato',
            'prediction': 'overripe',
            'confidence': 0.78
        },
        {
            'name': 'Scenario 4: Low Confidence',
            'fruit': 'orange',
            'prediction': 'ripe',
            'confidence': 0.45  # Below threshold
        }
    ]
    
    # Process each scenario
    for test in test_cases:
        print(f"\n{test['name']}")
        system.process_prediction(
            prediction=test['prediction'],
            confidence=test['confidence'],
            fruit_type=test['fruit']
        )
        time.sleep(2)  # Brief pause between scenarios
    
    # Display statistics
    print("\n📊 STATISTICS:")
    print("=" * 70)
    stats = system.get_statistics()
    print(f"Total predictions processed: {stats['total_predictions']}")
    print(f"Ripeness distribution: {stats['ripeness_distribution']}")
    print(f"Average confidence: {stats['average_confidence']:.1%}")
    
    # Save log
    print("\n💾 SAVING RESPONSE LOG:")
    print("=" * 70)
    system.save_log('response_log.json')
    
    # Shutdown
    system.shutdown()


if __name__ == '__main__':
    main()
