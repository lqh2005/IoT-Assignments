# 🍎 Assignment 16: Respond to Classification Results

Create an IoT system that **responds to fruit classification predictions** by controlling actuators and sending data to the cloud.

## 🎯 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Demo

```bash
# Main response system with test scenarios
python app.py

# Or test individual modules
python actuator_control.py    # Test LED, buzzer, relay
python iot_hub_sender.py      # Test IoT Hub messaging
```

### 3. Expected Output

```
🍎 Fruit Classifier Response System
======================================================================

📋 TEST SCENARIOS:
======================================================================

Scenario 1: Ripe Apple
======================================================================
  Fruit Type: apple
  Prediction: ripe
  Confidence: 92.0%
  Ripeness Classification: ripe

  🎛️ Controlling actuators...
    → led_green: ON
    → led_red: OFF
    → led_yellow: OFF
    → buzzer: OFF
  Message: ✅ Fruit is RIPE - Ready for harvest!

  📤 Sending to IoT Hub...
    ✅ Data sent to IoT Hub

...
```

## 📁 File Structure

```
Assignment_16/
├── app.py                      # Main response system
├── actuator_control.py         # LED, buzzer, relay control
├── iot_hub_sender.py          # Azure IoT Hub integration
├── assignment16.md             # Detailed observations
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔴 How It Works

### Decision Logic

```
Classifier Output: "ripe" (92% confidence)
                ↓
        Is confidence > 50%?
           ↙ YES      ↘ NO
        ↓              ↓
    RESPOND        DO NOTHING
      ↓
  Turn on GREEN LED
  Beep ONCE
  Send to cloud
  Message: "Ready to pick!"
```

### Ripeness States

| State | LED | Buzzer | Meaning |
|-------|-----|--------|---------|
| 🟢 Ripe | Green | 1 beep | Ready to harvest |
| 🔴 Unripe | Red | Silent | Too early, wait |
| 🟡 Overripe | Yellow | 2 beeps | Urgent, pick now |
| ⚫ Uncertain | Off | Silent | Cannot decide |

## 🎮 Actuator Control

### LEDs

```python
from actuator_control import ActuatorController

controller = ActuatorController()

# Control individual LEDs
controller.set_led('green', True)    # Turn ON green LED
controller.set_led('red', False)     # Turn OFF red LED
controller.set_led('yellow', True)   # Turn ON yellow LED
```

### Buzzer

```python
# Play sound
controller.buzzer(True, duration=0.5)   # 500ms beep
controller.buzzer(False)                # Stop sound
```

### Relay (for motor/pump)

```python
controller.relay(True)    # Activate relay
controller.relay(False)   # Deactivate relay
```

### Emergency Stop

```python
controller.emergency_stop()  # Turn off everything
```

## 📤 IoT Hub Integration

### Send Classification Data

```python
from iot_hub_sender import IoTHubSender, IoTHubMessageBuilder

sender = IoTHubSender('my-device-01')

# Build and send message
msg = IoTHubMessageBuilder.build_classification_message(
    device_id='my-device-01',
    fruit_type='apple',
    prediction='ripe',
    confidence=0.92,
    ripeness='ripe'
)

sender.send_message(msg)
```

### Send Alerts

```python
# Critical alert
sender.send_alert(
    alert_type='ripeness_reached',
    message='Fruit is now ripe',
    severity='warning'
)

# Info alert
sender.send_alert(
    alert_type='status_check',
    message='Device online',
    severity='info'
)
```

### Receive Messages from Cloud

```python
# Cloud-to-Device: Control device from cloud
received_msg = sender.receive_message()
if received_msg:
    if received_msg['command'] == 'change_threshold':
        # Update confidence threshold
        new_threshold = received_msg['value']
```

## 🧪 Test Examples

### Example 1: Process Single Prediction

```python
from app import FruitResponseSystem

system = FruitResponseSystem('device-001')

# Process prediction
response = system.process_prediction(
    prediction='ripe',
    confidence=0.92,
    fruit_type='apple'
)

print(f"Response: {response['actuator_response']['message']}")
```

### Example 2: Batch Processing

```python
from app import FruitResponseSystem

system = FruitResponseSystem('device-001')

# Multiple predictions
predictions = [
    {'fruit': 'apple', 'prediction': 'ripe', 'confidence': 0.92},
    {'fruit': 'banana', 'prediction': 'unripe', 'confidence': 0.87},
    {'fruit': 'tomato', 'prediction': 'overripe', 'confidence': 0.78},
]

log = system.continuous_monitoring(predictions)

# Get statistics
stats = system.get_statistics()
print(f"Total processed: {stats['total_predictions']}")
print(f"Distribution: {stats['ripeness_distribution']}")
```

### Example 3: Custom Alert Sequence

```python
from actuator_control import ActuatorController, ActuatorSequence

controller = ActuatorController()
sequence = ActuatorSequence(controller)

# Alert sequences
sequence.alert_sequence('info')        # Single green beep
sequence.alert_sequence('warning')    # Yellow + 3 beeps
sequence.alert_sequence('critical')   # Fast red blinking + long beep

# Harvest ready
sequence.harvest_ready_sequence()      # Green + beeps + conveyor ON
```

## ⚙️ Configuration

### Simulator vs Real Mode

```python
# Simulator mode (testing without hardware)
controller = ActuatorController(simulate=True)

# Real mode (Raspberry Pi GPIO)
controller = ActuatorController(simulate=False)
```

### Confidence Thresholds

Modify in `app.py`:

```python
def classify_ripeness(self, prediction, confidence):
    if confidence < 0.5:          # ← Change this threshold
        return "uncertain"
    # ...
```

Lower threshold = More sensitive (more false positives)  
Higher threshold = More conservative (fewer alerts)

## 📊 Output Files

Running the system generates:

1. **response_log.json** - All classification responses
2. **iot_messages.json** - All IoT Hub messages

Example response_log.json:
```json
{
  "device_id": "fruit-device-01",
  "timestamp": "2026-05-04T10:30:45",
  "responses": [
    {
      "classifier": {"prediction": "ripe", "confidence": 0.92},
      "classification": {"ripeness": "ripe"},
      "actuator_response": {
        "message": "✅ Fruit is RIPE - Ready for harvest!",
        "actuator_actions": [...]
      }
    }
  ],
  "statistics": {
    "total_predictions": 4,
    "ripeness_distribution": {"ripe": 2, "unripe": 1, "overripe": 1}
  }
}
```

## 🔌 Hardware Setup (Real Deployment)

### Wiring Diagram

```
Raspberry Pi GPIO
├─ Pin 17 → Red LED → Resistor (330Ω) → GND
├─ Pin 27 → Green LED → Resistor (330Ω) → GND
├─ Pin 22 → Yellow LED → Resistor (330Ω) → GND
├─ Pin 23 → Buzzer → GND
├─ Pin 24 → Relay IN → Motor/Pump → Power supply
└─ Pin 25 → Motor PWM → Motor speed control

All → Common GND with power supply
```

### Install GPIO Library

```bash
# For Raspberry Pi
pip install RPi.GPIO
# OR (recommended)
pip install gpiozero

# For other platforms
pip install PyGPIO
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| ImportError: RPi.GPIO | Not on Raspberry Pi or not installed. Use simulator mode. |
| "Permission denied" GPIO | Run with `sudo` or add user to `gpio` group |
| LED not lighting up | Check resistor value, pin assignment, polarity |
| Buzzer no sound | Check buzzer connection, might need amplifier |
| IoT Hub not working | Check connection string, network connectivity |

## 🎓 Learning Outcomes

After this assignment, you should understand:

1. ✅ How to make decisions based on ML predictions
2. ✅ Actuator control for IoT devices
3. ✅ Confidence thresholds and alert levels
4. ✅ IoT Hub cloud integration
5. ✅ Full IoT pipeline: Sense → Process → Decide → Act → Report

## 📚 Related Concepts

- **Decision Trees**: How to decide what action to take
- **Thresholding**: Setting confidence boundaries
- **State Machines**: Multiple states (ripe, unripe, overripe)
- **Real-time Systems**: Fast response requirements
- **Cloud Integration**: Sending data to Azure/AWS

## ✅ Rubric Checklist

- ✅ Respond to predictions (not just raw data)
- ✅ Make decisions based on ripeness
- ✅ Control actuators based on decision
- ✅ Send data to IoT Hub
- ✅ Log responses for audit
- ✅ Handle multiple test scenarios
- ✅ Comprehensive documentation

---

**Ready to test!** Run `python app.py` to see the system in action. 🚀
