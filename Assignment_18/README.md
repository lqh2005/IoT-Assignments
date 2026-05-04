# Fruit Quality Detector - Quick Start Guide

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings (or leave as defaults for simulator)
```

### 3. Run the System
```bash
python app.py
```

### 4. Run Tests
```bash
python integration_test.py
```

## 📦 Project Structure

```
Assignment_18/
├── app.py                      # Main detector orchestrator
├── proximity_monitor.py        # HC-SR04 distance sensor
├── camera_trigger.py          # USB camera control
├── cloud_storage.py           # Azure Blob Storage
├── integration_test.py        # Test suite
├── requirements.txt           # Python dependencies
├── .env.example               # Configuration template
├── assignment18.md            # Full documentation
└── README.md                  # This file
```

## 🎯 System Components

### Proximity Monitor
- **File:** `proximity_monitor.py`
- **Purpose:** Detect objects within trigger distance
- **Modes:** Real GPIO (RPi/Jetson) or Simulator
- **Trigger Distance:** 20cm (configurable)

### Camera Trigger
- **File:** `camera_trigger.py`
- **Purpose:** Capture images of detected objects
- **Modes:** Real USB camera or Synthetic generation
- **Resolution:** 640x480 (configurable)

### Edge Classification
- **Model:** MobileNetV2 + custom classifier head
- **Classes:** Fruit type + ripeness state
- **Latency:** ~50-100ms (on-edge inference)
- **Confidence:** Thresholding prevents false positives

### Cloud Storage
- **File:** `cloud_storage.py`
- **Purpose:** Store images and metadata in Azure
- **Modes:** Real Azure Blob or Local simulator
- **Features:** Auto-retry, metadata tracking

### LED Control
- **Green:** Ripe fruit
- **Red:** Unripe fruit
- **Yellow:** Overripe or low confidence
- **Buzzer:** Alert for overripe

### IoT Hub Integration
- **Purpose:** Send telemetry to cloud
- **Data:** Fruit type, ripeness, confidence, timestamp
- **Modes:** Real IoT Hub or Simulator

## 📝 Configuration

### Default Settings (Simulator Mode)

```python
# .env
SIMULATOR_MODE=true                          # Use simulators for testing
PROXIMITY_TRIGGER_DISTANCE=20                # cm
CAMERA_DEVICE_ID=0                          # USB camera index
DETECTION_INTERVAL=0.5                      # seconds between checks
```

### Real Hardware Settings

```python
# .env
SIMULATOR_MODE=false                        # Use real sensors

# Azure Storage
STORAGE_CONNECTION_STRING=DefaultEndpointProtocol=https;AccountName=...

# IoT Hub
IOT_HUB_CONNECTION_STRING=HostName=hub.azure.devices.net;SharedAccessKeyName=...

# Hardware
PROXIMITY_TRIGGER_DISTANCE=25               # Adjust for environment
CAMERA_DEVICE_ID=0                          # May be 0, 1, 2... depending on USB devices
```

## 🧪 Testing

### Run All Tests
```bash
python integration_test.py
```

**Output:**
```
✅ PASS: Proximity Monitor (Detected 1/10 objects)
✅ PASS: Camera Trigger (Captured 3 images)
✅ PASS: Cloud Storage (Uploaded and listed 3 blobs)
✅ PASS: Actuator Control (LED, buzzer, and relay working)
✅ PASS: IoT Hub Sender (Message sent successfully)
✅ PASS: Complete System (System ran for 1.2s, 2 detections)
```

### Manual Testing in Simulator Mode

```bash
# Terminal 1: Start the detector
python app.py

# Output:
# 2026-05-04 10:30:45 - root - INFO - Starting Fruit Quality Detector...
# 2026-05-04 10:30:46 - proximity_monitor - INFO - Object detected at 18.5cm
# 2026-05-04 10:30:46 - camera_trigger - INFO - Image captured: captures/apple_20260504_103046_123.jpg
# 2026-05-04 10:30:47 - app - INFO - Classification result: {'fruit': 'apple', 'ripeness': 'ripe', ...}
# ...

# Terminal 2: Check captured images
ls -la captures/

# Check uploaded files
ls -la cloud_storage/fruit-images/detections/

# Check results log
tail -f detection_results.jsonl
```

## 🔌 Hardware Deployment

### Raspberry Pi 4 with HC-SR04 + USB Camera

```bash
# 1. Enable GPIO
sudo raspi-config
# → Interface Options → GPIO → Enable

# 2. Install system dependencies
sudo apt-get update
sudo apt-get install python3-rpi.gpio libatlas-base-dev libjasper-dev

# 3. Run with GPIO
SIMULATOR_MODE=false python app.py
```

### NVIDIA Jetson Nano

```bash
# 1. GPIO is built-in, no setup needed

# 2. Install CUDA libraries for TensorFlow GPU acceleration
sudo apt-get install python3-tensorflow

# 3. Run detector (will use GPU for inference)
SIMULATOR_MODE=false python app.py
```

## 📊 Monitoring

### Check System Statistics

In the running detector output, you'll see:
```
Detection cycle complete
Detections: 3, Classifications: 3, Errors: 0, Uptime: 45.2s
```

### View Local Results

```bash
# Captured images
ls -la captures/

# Detection results (JSONL format - one result per line)
cat detection_results.jsonl

# Cloud storage mirror (local simulator mode)
ls -la cloud_storage/fruit-images/detections/
```

## 🐛 Troubleshooting

### No detections happening?
- Check `PROXIMITY_TRIGGER_DISTANCE` - may be too small
- Verify simulator is running (should see "Simulated distance" in logs)
- Check detection interval isn't too long

### Camera error?
```bash
# Test camera directly
python -c "import cv2; c=cv2.VideoCapture(0); print(c.isOpened())"
```

### Azure Storage not working?
- Check connection string in `.env`
- Verify Azure Storage account exists
- Try `SIMULATOR_MODE=true` to use local storage

### LED not blinking?
- Verify GPIO pins in hardware setup
- Check LED configuration (active high/low)
- Use `simulator_mode=True` for testing

## 📈 Performance Tips

1. **Faster classification:** Use smaller images (320x240)
2. **More detections:** Lower `PROXIMITY_TRIGGER_DISTANCE`
3. **Less cloud traffic:** Increase `DETECTION_INTERVAL`
4. **GPU acceleration:** Run on NVIDIA Jetson Nano
5. **Offline operation:** Local storage queues when no internet

## 🎓 Learning Resources

- **Assignment 15 (Classification):** See model training details
- **Assignment 16 (Response System):** See decision logic and LED control
- **Assignment 17 (Edge Deployment):** See Docker containerization
- **assignment18.md:** Full technical documentation

## ✅ Submission Checklist

Before submitting, ensure:

- [ ] All components initialized correctly
- [ ] Integration tests passing
- [ ] No Python errors in logs
- [ ] Can capture and classify images
- [ ] LED feedback working
- [ ] Local storage has results
- [ ] Documentation complete

## 📚 API Reference

### FruitQualityDetector Class

```python
from app import FruitQualityDetector

# Initialize
detector = FruitQualityDetector(config=None)

# Run detector (blocking)
detector.run()

# Get statistics
stats = detector.get_statistics()
# Returns: {'detections': 5, 'classifications': 5, 'errors': 0, ...}

# Graceful shutdown
detector.shutdown()
```

### ProximityMonitor Class

```python
from proximity_monitor import ProximityMonitor

monitor = ProximityMonitor(trigger_distance=20, simulator_mode=True)
distance, detected = monitor.measure()  # (cm, bool)
stats = monitor.get_statistics()
monitor.cleanup()
```

### CameraTrigger Class

```python
from camera_trigger import CameraTrigger

camera = CameraTrigger(simulator_mode=True)
image_path = camera.capture()
stats = camera.get_statistics()
camera.cleanup()
```

### CloudStorageManager Class

```python
from cloud_storage import CloudStorageManager

storage = CloudStorageManager(
    connection_string="...",
    container_name="fruit-images",
    simulator_mode=True
)
success = storage.upload_blob("local.jpg", "cloud/image.jpg")
blobs = storage.list_blobs()
stats = storage.get_statistics()
storage.cleanup()
```

## 🚀 Next Steps

1. **Customize fruit types:** Modify classification logic in `app.py`
2. **Add more sensors:** Humidity, temperature, pH sensors
3. **Extend storage:** Add database integration
4. **Mobile app:** Create React app to view detections
5. **Analytics:** Dashboard showing detection trends

---

**Questions?** Check `assignment18.md` for detailed documentation!
