# Hardware Setup Guide - Raspberry Pi & Jetson Nano

## 🎛️ Raspberry Pi 4 Setup

### Hardware Requirements
- Raspberry Pi 4 (2GB RAM minimum, 4GB recommended)
- 32GB microSD card (Class 10)
- 5V 3A USB-C power supply
- USB camera (or Pi Camera v2)
- Ethernet cable or WiFi (built-in)

### Initial Setup

#### Step 1: Flash Operating System
```bash
# Download Raspberry Pi Imager
# https://www.raspberrypi.com/software/

# Use Imager to:
# 1. Select "Raspberry Pi OS Lite" (64-bit)
# 2. Select your microSD card
# 3. Advanced options:
#    - Enable SSH
#    - Set hostname: raspberrypi
#    - Configure WiFi
# 4. Flash and wait (5-10 minutes)
```

#### Step 2: Boot and Connect
```bash
# Insert microSD card into Pi
# Connect power (activity LED blinks during boot)
# Wait 30 seconds for first boot

# Connect from PC
ssh pi@raspberrypi.local
# Default password: raspberry
```

#### Step 3: Update System
```bash
# On Raspberry Pi terminal
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-dev
sudo apt-get install -y libatlas-base-dev libjasper-dev libtiff5
```

#### Step 4: Setup Python Environment
```bash
# Create project directory
mkdir ~/fruit_detector
cd ~/fruit_detector

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### Step 5: Install TensorFlow
```bash
# On Raspberry Pi (takes 10-15 minutes)
# Note: Official TensorFlow has performance issues on ARM
# Better option: Use pre-built wheels

# Option A: Official (slower but guaranteed to work)
pip install tensorflow

# Option B: Faster (community-built)
pip install https://github.com/PINTO0309/TensorflowLite-bin/releases/download/v2.12.0/tensorflow-2.12.0-cp39-none-linux_armv7l.whl
```

#### Step 6: Install Project Dependencies
```bash
# Copy requirements.txt from PC
scp requirements.txt pi@raspberrypi.local:~/fruit_detector/

# Install on Pi
cd ~/fruit_detector
pip install -r requirements.txt
# This may take 20-30 minutes on Pi
```

#### Step 7: Copy Model
```bash
# From PC
scp exported_models/fruit_detector_int8.tflite \
  pi@raspberrypi.local:~/fruit_detector/

# Verify on Pi
ls -lh ~/fruit_detector/fruit_detector_int8.tflite
# Should show size around 12MB
```

#### Step 8: Setup Camera
```bash
# On Raspberry Pi
sudo raspi-config

# Navigate to:
# Interface Options → Camera → Enable
# Reboot

# Test camera
libcamera-hello --list-cameras
```

#### Step 9: Test Inference
```bash
# SSH into Pi
ssh pi@raspberrypi.local
cd ~/fruit_detector
source venv/bin/activate

# Quick test
python3 << 'EOF'
from edge_runtime import EdgeInferenceServer

server = EdgeInferenceServer('fruit_detector_int8.tflite')
print("✅ Model loaded on Raspberry Pi!")
print(f"Input shape: {server.input_details[0]['shape']}")
EOF
```

## 🖥️ NVIDIA Jetson Nano Setup

### Hardware Requirements
- NVIDIA Jetson Nano Dev Kit (4GB)
- 64GB microSD card (Class 10, high endurance)
- 5V 4A power supply with barrel connector
- USB camera
- Ethernet or WiFi dongle

### Initial Setup

#### Step 1: Flash Jetson Image
```bash
# Download NVIDIA SD card image
# https://developer.nvidia.com/jetson-nano-sd-card-image

# Flash with:
# - Balena Etcher (GUI) or
# - dd command (terminal)

# Wait for completion (15-20 minutes)
```

#### Step 2: Boot and Initial Configuration
```bash
# Power on Jetson
# Connect HDMI monitor and USB keyboard
# Follow on-screen setup wizard:
#   - Accept terms
#   - Create user account
#   - Connect WiFi
# Device will reboot
```

#### Step 3: Update System
```bash
# SSH or terminal on Jetson
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.8+
sudo apt-get install -y python3-pip python3-dev

# Jetson already has CUDA, cuDNN, and TensorRT installed
```

#### Step 4: Install TensorFlow
```bash
# NVIDIA provides pre-built TensorFlow wheels
# For Jetson Nano, use TensorFlow 2.x

# Option A: Using pip (recommended)
sudo pip install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v50 tensorflow

# Option B: Using Docker (alternative)
docker run --runtime nvidia -it --rm \
  -v ~/fruit_detector:/workspace \
  nvcr.io/nvidia/tensorflow:21.02-tf2-py3
```

#### Step 5: Setup Project
```bash
# Create project directory
mkdir ~/fruit_detector
cd ~/fruit_detector

# Create virtual environment (optional on Jetson)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 6: Copy and Test Model
```bash
# Copy model to Jetson (same as Pi)
scp exported_models/fruit_detector_int8.tflite \
  nvidia@jetson.local:~/fruit_detector/

# Test on GPU
python3 << 'EOF'
import tensorflow as tf

# Verify GPU
gpus = tf.config.list_physical_devices('GPU')
print(f"GPUs available: {len(gpus)}")
if gpus:
    for gpu in gpus:
        print(f"  {gpu}")

# Test inference
from edge_runtime import EdgeInferenceServer
server = EdgeInferenceServer('fruit_detector_int8.tflite')
result = server.infer('test.jpg')
print(f"✅ GPU inference: {result['inference_time_ms']:.2f}ms")
EOF
```

## 🔧 GPIO & Sensor Setup

### Raspberry Pi GPIO Pinout

```
     ┌─────────────────────┐
     │ USB Ports           │
     │   (Top)             │
     ├─────────────────────┤
     │ 3.3V  5V  GND       │
     │ GPIO2 GPIO3  GND    │  I2C
     │ GPIO4  GND          │
     │ GPIO17 GPIO27 GND   │
     │ GPIO22 GPIO10 GPIO9 │
     │ GPIO11 GND          │
     │                     │
     │ GPIO5 GPIO6  GND    │
     │ GPIO12 GPIO13 GND   │
     │ GPIO19 GPIO26 GPIO20│
     │ GPIO21 GND          │
     └─────────────────────┘
     Raspberry Pi 4
```

### HC-SR04 Ultrasonic Sensor Connection

```
     ┌──────────────┐
     │  HC-SR04     │
     │  ┌────────┐  │
     ├─ │TRIG  VCC├─┼── 5V
     ├─ │ECHO GND├─┼── GND
     │  └────────┘  │
     └──────────────┘
           ▼
     ┌─────────────┐
     │ Level       │
     │ Shifter     │  (5V to 3.3V)
     │ 74LVC245    │
     └─────────────┘
           ▼
     Raspberry Pi GPIO:
     - TRIG: GPIO 23
     - ECHO: GPIO 24 (through level shifter)
```

### LED Connection

```
Raspberry Pi                 LEDs
─────────────────────────────────
GPIO 17 ─────────────────→ Green LED (anode)
GPIO 27 ─────────────────→ Red LED (anode)
GPIO 22 ─────────────────→ Yellow LED (anode)

All LED cathodes → GND (with 220Ω resistors)
```

## 📋 Troubleshooting Setup

| Problem | Solution |
|---------|----------|
| Can't SSH to Pi | Check network, use `ping raspberrypi.local` |
| Python too slow on Pi | Use int8 TFLite model, reduce image size |
| Out of memory | Increase swap: `sudo dphys-swapfile swapoff/swapon` |
| Camera not detected | Run `libcamera-hello --list-cameras` |
| Model inference crashes | Check image format (RGB not RGBA) |
| Jetson runs out of memory | Use GPU model or reduce batch size |

## ⚡ Performance Monitoring

### On Raspberry Pi

```bash
# Monitor CPU temperature
watch -n 1 vcgencmd measure_temp

# Monitor RAM usage
free -h

# Monitor processes
htop
```

### On Jetson Nano

```bash
# Monitor GPU & CPU (built-in tool)
jtop

# Or system stats
nvidia-smi
```

## 🎓 Quick Reference

### Raspberry Pi Checklist
- [ ] OS flashed on microSD
- [ ] SSH working
- [ ] Python 3.9+ installed
- [ ] TensorFlow installed
- [ ] Model copied
- [ ] Camera connected
- [ ] GPIO tested
- [ ] Inference working

### Jetson Nano Checklist
- [ ] OS flashed on microSD
- [ ] System updated
- [ ] Python 3.8+ installed
- [ ] TensorFlow with GPU support
- [ ] Model copied
- [ ] GPU acceleration verified
- [ ] Inference tested
- [ ] Performance benchmarked

## 📚 Next Steps

1. **Setup complete?** → Run edge_runtime.py
2. **Need real-time detection?** → Integrate with camera capture
3. **Need cloud sync?** → Setup Azure IoT Hub
4. **Need LED control?** → Add GPIO control code

---

**Remember:** Deployment takes patience. Test each step before moving to the next!
