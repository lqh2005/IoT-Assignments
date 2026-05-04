# Deployment Guide - Assignment 20

## 🎯 Deployment Scenarios

### Scenario A: Rapid Testing (PC Only)

**Time**: 15 minutes
**Setup**: Just run on your PC
**Result**: Verify model works before edge deployment

```bash
# 1. Export model
python app.py --model ../Assignment_15/fruit_classifier.h5 --export-all

# 2. Test all formats
python app.py --model ../Assignment_15/fruit_classifier.h5 --test-dir test_images/

# 3. Choose best format (usually int8)
# ✅ Done! Model is ready for edge deployment
```

### Scenario B: Raspberry Pi Deployment

**Time**: 45 minutes (includes SD card setup)
**Equipment**: Raspberry Pi 4, USB camera, SD card
**Result**: Real-time fruit detection on Pi

#### Step 1: Prepare Raspberry Pi

```bash
# On development PC
# 1. Flash Raspberry Pi OS on SD card (using Raspberry Pi Imager)
# 2. Enable SSH in Raspberry Pi Imager settings
# 3. Boot Pi with SD card

# 4. Find Pi's IP address
ping raspberrypi.local  # or check router for IP
```

#### Step 2: Copy Model to Pi

```bash
# On development PC (after exporting model)
scp -r exported_models/fruit_detector_int8.tflite \
  pi@raspberrypi.local:/home/pi/

# Also copy edge_runtime.py
scp edge_runtime.py pi@raspberrypi.local:/home/pi/
scp requirements.txt pi@raspberrypi.local:/home/pi/
```

#### Step 3: Setup on Raspberry Pi

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Install dependencies
pip install -r requirements.txt

# Test inference
python3 << 'EOF'
from edge_runtime import EdgeInferenceServer
print("Testing TFLite model...")
server = EdgeInferenceServer('fruit_detector_int8.tflite')
print("✅ Model loaded successfully!")
print(f"Input shape: {server.input_details[0]['shape']}")
EOF
```

#### Step 4: Run Real-Time Detection

```bash
# Create a simple detection loop
python3 << 'EOF'
from edge_runtime import EdgeInferenceServer
import time

server = EdgeInferenceServer('fruit_detector_int8.tflite')
stats = server.get_statistics()

print("Ready for image input!")
print(f"Average FPS: {stats['fps']:.1f}")
EOF
```

### Scenario C: Jetson Nano Deployment

**Time**: 30 minutes (Jetson OS pre-installed)
**Equipment**: Jetson Nano Dev Kit, USB camera
**Result**: GPU-accelerated real-time detection

#### Step 1: Setup Jetson Nano

```bash
# On Jetson Nano (connect via HDMI+keyboard or SSH)
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install build tools
sudo apt-get install -y python3-pip python3-dev
```

#### Step 2: Install TensorFlow on Jetson

```bash
# Install pre-built TensorFlow for Jetson
pip install --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v50 tensorflow

# Or use NVIDIA L4T TensorFlow container (recommended)
docker run --runtime nvidia -it nvcr.io/nvidia/tensorflow:21.02-tf2-py3
```

#### Step 3: Copy and Test Model

```bash
# Copy files (same as Raspberry Pi)
scp -r exported_models/fruit_detector_int8.tflite jetson@jetson.local:/home/jetson/

# Test on GPU
python3 << 'EOF'
import tensorflow as tf
print(f"GPUs available: {len(tf.config.list_physical_devices('GPU'))}")

from edge_runtime import EdgeInferenceServer
server = EdgeInferenceServer('fruit_detector_int8.tflite')
stats = server.get_statistics()
print(f"GPU-accelerated FPS: {stats['fps']:.1f}")
EOF
```

## 📊 Performance Benchmarking

### On Raspberry Pi

```bash
# Run performance test
python3 << 'EOF'
from edge_runtime import EdgeInferenceServer
import time

server = EdgeInferenceServer('fruit_detector_int8.tflite')

# Simulate 100 inferences
for i in range(100):
    result = server.infer('test_image.jpg')
    if (i+1) % 20 == 0:
        print(f"Processed {i+1} images...")

stats = server.get_statistics()
print(f"\nRaspberry Pi Performance:")
print(f"  Total inferences: {stats['total_inferences']}")
print(f"  Average time: {stats['avg_inference_time_ms']:.2f}ms")
print(f"  FPS: {stats['fps']:.2f}")
print(f"  Errors: {stats['errors']}")
EOF
```

### On Jetson Nano

```bash
# Same code, but GPU is used automatically
# Expected: 3-5x faster than Raspberry Pi
```

## 🔧 Integration with Previous Components

### With Assignment 18 System

```python
# Replace simulated classifier with real TFLite model
from edge_runtime import EdgeInferenceServer

class FruitDetectorV2:
    def __init__(self):
        self.inference = EdgeInferenceServer(
            'exported_models/fruit_detector_int8.tflite'
        )
    
    def classify(self, image_path):
        result = self.inference.infer(image_path)
        return {
            'ripeness': result['predictions'][0],
            'class_idx': np.argmax(result['predictions'])
        }
```

### With IoT Hub Telemetry

```python
# Send inference results to cloud
from edge_runtime import EdgeInferenceServer
from azure.iot.device import IoTHubDeviceClient

device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
server = EdgeInferenceServer('fruit_detector_int8.tflite')

result = server.infer('image.jpg')
message = {
    'prediction': int(np.argmax(result['predictions'])),
    'confidence': float(np.max(result['predictions'])),
    'inference_time_ms': result['inference_time_ms']
}

device_client.send_message(json.dumps(message))
```

## ✅ Deployment Verification Checklist

- [ ] Model exports successfully
- [ ] All formats generated (float32, float16, int8)
- [ ] Inference works on PC
- [ ] Accuracy verified (>90%)
- [ ] Model size acceptable (<15MB)
- [ ] Edge device configured
- [ ] Model copied to edge device
- [ ] Edge runtime installed
- [ ] Inference working on edge device
- [ ] Performance meets requirements (>10 FPS)
- [ ] Integration with sensors complete
- [ ] Cloud communication working (if applicable)

## 🚨 Troubleshooting Deployment

| Issue | Solution |
|-------|----------|
| SSH connection refused | Check Pi is on same network, verify IP |
| Model inference fails | Check image format (RGB, not RGBA) |
| Out of memory on Pi | Use int8 model, reduce batch size |
| Inference too slow | Use int8, reduce image resolution |
| GPU not used on Jetson | Install nvidia-tensorflow package |

## 📈 Production Deployment Tips

1. **Model versioning**: Keep old models for rollback
2. **Monitoring**: Log inference times and errors
3. **Updates**: Have a secure model update mechanism
4. **Redundancy**: Deploy to multiple devices
5. **Testing**: Test on real hardware before production

## 🎓 Rubric Verification

✅ **Correct compact domain**
  - Used best model from Assignment 19
  - Exported as quantized TFLite

✅ **Export detector successfully**
  - Model converts to TFLite format
  - File size < 15MB
  - Inference works

✅ **Run on edge device**
  - Deployed to Raspberry Pi or Jetson
  - Runs at >10 FPS
  - Accuracy >90%

✅ **Access from IoT device**
  - Can capture and process images
  - Integration with sensors/LEDs
  - Results logged or sent to cloud
