# Hardware Setup Guide

## 🔧 Complete Hardware Configuration

### Option 1: Raspberry Pi 4 (Recommended)

#### Requirements
- Raspberry Pi 4 (2GB RAM minimum, 4GB recommended)
- Raspberry Pi OS (Bullseye or newer)
- HC-SR04 Ultrasonic Sensor
- USB Webcam
- RGB LED (or 3 separate LEDs)
- Buzzer (passive)
- Relay module (optional, for motors)
- Breadboard and jumper wires
- 330Ω resistors (for LEDs)

#### GPIO Pin Layout

```
Raspberry Pi GPIO (BCM Numbering)
┌─────────────────────────────────┐
│  3.3V ───────── LED VCC (via R)  │
│  5V   ───────── HC-SR04 VCC      │
│  GND  ───────── All GND          │
│                                  │
│  GPIO 17 ─ LED GREEN (via 330Ω) │
│  GPIO 22 ─ LED YELLOW (via 330Ω)│
│  GPIO 27 ─ LED RED (via 330Ω)   │
│  GPIO 26 ─ BUZZER (+)            │
│  GPIO 23 ─ HC-SR04 TRIG          │
│  GPIO 24 ─ HC-SR04 ECHO          │
└─────────────────────────────────┘
```

#### Detailed Wiring

**HC-SR04 Ultrasonic Sensor:**
```
HC-SR04 → Raspberry Pi
VCC     → 5V (Pin 2 or 4)
GND     → GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
TRIG    → GPIO 23 (Pin 16)
ECHO    → GPIO 24 (Pin 18) [Use level shifter to 3.3V]
```

**⚠️ IMPORTANT: Level Shifter for ECHO**
- HC-SR04 ECHO outputs 5V
- RPi GPIO expects max 3.3V
- Use voltage divider: 1kΩ + 2kΩ resistors
```
HC-SR04 ECHO ──[1kΩ]──┬──[2kΩ]── GND
                       │
                       └─→ GPIO 24
```

**RGB LED:**
```
LED Common Cathode (RGB LED):
Red    ──[330Ω]── GPIO 27
Green  ──[330Ω]── GPIO 17
Blue   ──[330Ω]── GPIO 22
GND    ───────── GND
```

**Passive Buzzer:**
```
Buzzer+ ──── GPIO 26
Buzzer- ──── GND
```

#### Software Setup

```bash
# 1. Update system
sudo apt-get update && sudo apt-get upgrade

# 2. Enable GPIO interface
sudo raspi-config
# → Interface Options → GPIO → Enable

# 3. Install Python dependencies
sudo apt-get install python3-pip python3-dev python3-rpi.gpio libatlas-base-dev

# 4. Install Python packages
pip3 install -r requirements.txt

# 5. Run detector (may need sudo for GPIO)
sudo python3 app.py
```

### Option 2: NVIDIA Jetson Nano

#### Requirements
- NVIDIA Jetson Nano Developer Kit
- Jetpack OS (4.6 or newer)
- 2x USB 3.0 cameras (for better throughput)
- HC-SR04 Sensor
- RGB LED
- Buzzer

#### GPIO Pin Layout

```
Jetson Nano GPIO (NVIDIA numbering)
Same as Raspberry Pi (BCM compatible)
```

#### Software Setup

```bash
# 1. Install CUDA support
sudo apt-get install cuda-11-4

# 2. Install Python packages
pip3 install -r requirements.txt

# 3. Enable GPU acceleration for TensorFlow
pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v461 tensorflow

# 4. Run detector (automatically uses GPU)
python3 app.py
```

### Option 3: X86 PC (Development/Testing)

#### Requirements
- Windows/Linux/macOS PC
- USB Webcam
- (Optional) USB I2C adapter for sensors

#### Software Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run in simulator mode (no hardware needed)
SIMULATOR_MODE=true python app.py
```

## 📊 Sensor Specifications

### HC-SR04 Ultrasonic Sensor

| Property | Value |
|----------|-------|
| Operating Voltage | 5V DC |
| Operating Current | 15mA |
| Operating Frequency | 40kHz |
| Measurement Range | 2cm - 400cm |
| Accuracy | ±1cm |
| Resolution | ~0.3cm |
| Trigger Pulse | 10μs (min) |
| Response Time | 60ms |

**Working Principle:**
1. Send 10μs pulse to TRIG pin
2. Module sends 40kHz ultrasonic waves
3. Waves reflect off object
4. ECHO pin goes HIGH when receiving
5. Pulse duration = 2 × distance / speed_of_sound

### USB Camera Specifications

| Property | Value |
|----------|-------|
| Interface | USB 2.0/3.0 |
| Resolution | 640×480 (min) to 1920×1080 (max) |
| Frame Rate | 30 FPS (typical) |
| Auto-Focus | Yes (most cameras) |
| Power Draw | 500mA (typical) |

## 🔌 Breadboard Wiring Guide

### Complete Circuit Diagram (ASCII)

```
5V ────────────────────────────────── HC-SR04 VCC
                                      
3.3V ── LED_R ──[330Ω]── GPIO27(Red LED)
     ── LED_G ──[330Ω]── GPIO17(Green LED)
     ── LED_Y ──[330Ω]── GPIO22(Yellow LED)
     
GPIO23 ──────────────────── HC-SR04 TRIG
GPIO24 ──[1kΩ]──┬──[2kΩ]── GND  (Level Shifted ECHO)
               HC-SR04 ECHO
               
GPIO26 ──────────────────── BUZZER+

All GND ────────────────── HC-SR04 GND, BUZZER-, LED Cathodes
```

## ✅ Testing Hardware

### Test HC-SR04 Sensor

```bash
python3 -c "
from proximity_monitor import ProximityMonitor
pm = ProximityMonitor(simulator_mode=False)
for i in range(5):
    distance, detected = pm.measure()
    print(f'Distance: {distance:.1f}cm, Detected: {detected}')
pm.cleanup()
"
```

### Test Camera

```bash
python3 -c "
import cv2
cam = cv2.VideoCapture(0)
ret, frame = cam.read()
if ret:
    cv2.imwrite('test.jpg', frame)
    print('Camera works!')
else:
    print('Camera failed!')
cam.release()
"
```

### Test GPIO

```bash
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.HIGH)
print('GPIO 27 set HIGH')
GPIO.cleanup()
"
```

## 🐛 Troubleshooting Hardware

| Problem | Solution |
|---------|----------|
| **HC-SR04 not detecting** | Check voltage (5V), verify connections, test with oscilloscope |
| **Camera not found** | Try `ls /dev/video*`, check USB power, try different port |
| **LED not lighting** | Verify polarity, check resistor value, test with multimeter |
| **GPIO permission denied** | Run with `sudo` or add user to `gpio` group |
| **Noise in distance reading** | Add capacitor (0.1μF) near sensor, use multiple measurements |
| **Buzzer too quiet** | Use active buzzer instead, increase GPIO voltage |

## 📈 Performance Tuning

### For Faster Classification
```bash
# Use smaller image resolution
CAMERA_HEIGHT=320 CAMERA_WIDTH=240 python app.py
```

### For More Sensitive Detection
```bash
# Lower trigger distance threshold
PROXIMITY_TRIGGER_DISTANCE=15 python app.py
```

### For Lower Power Consumption
```bash
# Increase detection interval
DETECTION_INTERVAL=2.0 python app.py
```

## 🔒 Safety Considerations

1. **Power Supply:** Use proper 5V 2A power supply for RPi + sensors
2. **Heat Dissipation:** Add heatsinks to RPi on hot days
3. **Over-voltage Protection:** Use resistor dividers for 5V→3.3V signals
4. **Electrical Isolation:** Keep sensor and LED circuits separate
5. **Cable Management:** Secure cables to avoid accidental disconnection

## 📚 Additional Resources

- [Raspberry Pi GPIO Documentation](https://www.raspberrypi.com/documentation/)
- [HC-SR04 Datasheet](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf)
- [Jetson Nano GPIO Guide](https://developer.nvidia.com/embedded/learn/jetson-nano-2gb-devkit)
