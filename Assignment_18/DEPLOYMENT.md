# Deployment Checklist - Assignment 18

## 📋 Pre-Deployment Checklist

### Code Quality
- [ ] All Python files validated (no syntax errors)
- [ ] Import statements verified
- [ ] Logging configured and tested
- [ ] Error handling in place for all components
- [ ] No hardcoded credentials (using .env)

### Testing
- [ ] All integration tests passing (`python integration_test.py`)
- [ ] Individual components tested:
  - [ ] Proximity Monitor
  - [ ] Camera Trigger
  - [ ] Classification
  - [ ] LED Control
  - [ ] IoT Hub Sender
  - [ ] Cloud Storage
- [ ] System tested end-to-end in simulator mode

### Configuration
- [ ] `.env` file created with correct credentials
- [ ] All Azure connection strings validated
- [ ] Hardware pins configured for target device
- [ ] Detection parameters tuned

### Documentation
- [ ] `assignment18.md` reviewed and accurate
- [ ] `README.md` provides clear quick-start
- [ ] `hardware_setup.md` matches actual wiring
- [ ] Code comments added for clarity

## 🚀 Deployment Steps

### Step 1: Prepare Target Device

**For Raspberry Pi:**
```bash
# SSH into device
ssh pi@raspberrypi.local

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Enable GPIO
sudo raspi-config
# → Interface Options → GPIO → Enable → Yes → OK → Finish

# Install dependencies
sudo apt-get install python3-pip python3-dev python3-rpi.gpio libatlas-base-dev -y
```

**For NVIDIA Jetson:**
```bash
# SSH into device
ssh nvidia@jetson.local

# Update CUDA (if needed)
sudo apt-get update

# Install dependencies
sudo apt-get install python3-pip python3-dev -y
```

### Step 2: Upload Code

**Option A: Git Clone**
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/IoT-Assignments.git
cd IoT-Assignments/Assignment_18
```

**Option B: SCP**
```bash
# From local machine
scp -r Assignment_18/* pi@raspberrypi.local:/home/pi/fruit_detector/
```

### Step 3: Install Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import tensorflow; import cv2; print('OK')"
```

### Step 4: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit with credentials
nano .env

# Verify configuration
python3 -c "from config import get_config; c = get_config(); c.print_summary()"
```

### Step 5: Run Tests

```bash
# Run integration tests
python3 integration_test.py

# All tests should show ✅ PASS
```

### Step 6: Start Detector

**Simulator Mode (Testing):**
```bash
python3 app.py
# Ctrl+C to stop
```

**Real Hardware Mode:**
```bash
# May need sudo for GPIO
sudo python3 app.py

# Or add user to gpio group (one-time setup)
sudo usermod -a -G gpio $USER
newgrp gpio
python3 app.py
```

### Step 7: Monitor Execution

**In separate SSH session:**

```bash
# Watch logs
tail -f fruit_detector.log

# Check system stats
ps aux | grep python3

# Check storage
du -sh cloud_storage/
ls -la captures/
```

## 📊 Monitoring During Operation

### Check System Statistics
```bash
# View detection log
cat detection_results.jsonl | tail -5

# Count detections per hour
grep -c "ripe" detection_results.jsonl

# Check LED state
grep "LED:" fruit_detector.log | tail -10
```

### Performance Metrics

**Expected Performance:**
- Proximity detections: 1-3 per minute
- Classification latency: ~100ms
- Cloud upload latency: ~500ms
- System uptime: 99%+

**Check actual performance:**
```bash
# Duration between first and last detection
head -1 detection_results.jsonl
tail -1 detection_results.jsonl

# Calculate detection rate
# (last_time - first_time) / detection_count
```

## 🚨 Troubleshooting Deployment

### Issue: GPIO Permission Denied

**Solution:**
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Log out and back in
exit
# SSH again

# Verify
groups  # Should include 'gpio'
```

### Issue: Low Memory

**Solution:**
```bash
# Check memory usage
free -h

# If low, stop unnecessary services
sudo systemctl stop cups
sudo systemctl stop avahi-daemon

# Or reduce Python process
DETECTION_INTERVAL=2.0 python3 app.py
```

### Issue: Camera Not Detected

**Solution:**
```bash
# List camera devices
ls /dev/video*

# Test camera
python3 -c "import cv2; c=cv2.VideoCapture(0); print(c.isOpened())"

# Try different device ID
CAMERA_DEVICE_ID=1 python3 app.py
```

### Issue: Cloud Storage Upload Failing

**Solution:**
```bash
# Check Azure credentials
grep STORAGE_CONNECTION_STRING .env

# Test connection
python3 -c "from azure.storage.blob import BlobServiceClient; print('OK')"

# Or use simulator mode
SIMULATOR_MODE=true python3 app.py
```

## 📈 Production Optimization

### For Better Performance

```bash
# Reduce detection interval for more frequent checks
DETECTION_INTERVAL=0.2 python3 app.py

# Increase confidence threshold to reduce false positives
# (edit config.py: confidence_threshold=0.75)

# Use GPU if available
# (Jetson Nano will automatically use GPU)
```

### For Lower Resource Usage

```bash
# Increase detection interval to reduce CPU
DETECTION_INTERVAL=2.0 python3 app.py

# Reduce camera resolution
CAMERA_WIDTH=320 CAMERA_HEIGHT=240 python3 app.py

# Disable cloud uploads if not needed
SIMULATOR_MODE=true python3 app.py
```

### For Better Reliability

```bash
# Run with auto-restart on failure
# Create systemd service file:
sudo nano /etc/systemd/system/fruit-detector.service
```

**Service file content:**
```ini
[Unit]
Description=Fruit Quality Detector
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/fruit_detector
Environment="PATH=/home/pi/fruit_detector/venv/bin"
ExecStart=/home/pi/fruit_detector/venv/bin/python app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable fruit-detector.service
sudo systemctl start fruit-detector.service
sudo systemctl status fruit-detector.service
```

## 📋 Final Verification

Before declaring deployment complete:

- [ ] System runs without errors for 1 hour
- [ ] Detection events logged correctly
- [ ] Cloud uploads working
- [ ] LED feedback visible
- [ ] No memory leaks
- [ ] Logs are readable and useful
- [ ] System survives reboot

**Verification script:**
```bash
# Run for 1 hour
timeout 3600 python3 app.py

# Check results
echo "Detections: $(wc -l < detection_results.jsonl)"
echo "Errors: $(grep ERROR fruit_detector.log | wc -l)"
echo "Cloud uploads: $(ls cloud_storage/fruit-images/detections/ | wc -l)"
```

## 🎯 Success Criteria

✅ **Deployment is successful when:**
- All components initialized without errors
- Proximity detection working (objects detected)
- Images captured with timestamps
- Classification results logged
- LED feedback visible/audible
- Results stored locally and in cloud
- System stable for extended operation

---

**Deployment Guide Complete!** 🚀
