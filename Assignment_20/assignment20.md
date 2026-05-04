# Assignment 20: Use Your Fruit Detector on the Edge

## 📋 Overview

Deploy your trained fruit quality detector to edge devices (Raspberry Pi, Jetson Nano) by exporting it as a compact TensorFlow Lite model. This assignment focuses on **model optimization** and **edge deployment** of the classifier you built in previous assignments.

### Learning Objectives

After completing this assignment, you will:

1. **Export trained models** to multiple formats (SavedModel, TFLite)
2. **Optimize models** for edge devices (quantization, compression)
3. **Deploy to edge** - Run on Raspberry Pi/Jetson Nano
4. **Measure performance** - Latency, FPS, memory usage on hardware
5. **Understand trade-offs** - Accuracy vs size vs speed optimization

## 🎯 Rubric Mapping

| Criteria | Exemplary | Adequate | Needs Improvement |
|----------|-----------|----------|------------------|
| **Deploy detector to edge** | ✅ Use correct compact domain, export, run on edge | ⚠️ Export but cannot run on edge | ❌ Cannot export or run |
| **Export compact model** | ✅ TFLite format, multiple quantization levels | ⚠️ TFLite format only | ❌ Cannot export |
| **Run on IoT device** | ✅ Working on real hardware, access from device | ⚠️ Can run but cannot access | ❌ Cannot run |

## 🚀 Workflow

```
┌──────────────────────────────┐
│  Trained Keras Model         │
│  (From Assignment 15/19)     │
└──────────────┬───────────────┘
               │
               ▼
     ┌─────────────────────┐
     │ Export to Formats   │
     │ • SavedModel        │
     │ • TFLite (float32)  │
     │ • TFLite (float16)  │
     │ • TFLite (int8)     │
     └──────────┬──────────┘
                │
                ▼
     ┌──────────────────────┐
     │ Model Sizes:         │
     │ • Original: 140MB    │
     │ • SavedModel: 135MB  │
     │ • TFLite float: 45MB │
     │ • TFLite int8: 12MB  │
     └──────────┬───────────┘
                │
                ▼
    ┌────────────────────────┐
    │ Deploy to Edge Device  │
    │ • Raspberry Pi         │
    │ • Jetson Nano          │
    │ • Other ARM/Linux      │
    └────────────┬───────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │ Run Inference          │
    │ • Load TFLite model    │
    │ • Preprocess image     │
    │ • Run prediction       │
    │ • Measure performance  │
    └────────────────────────┘
```

## 📦 Model Export Formats

### 1. SavedModel (Full Precision)
```
Format: Directory with model structure
Size: ~95% of original
Inference: Standard TensorFlow
Use: Compatibility, fine-tuning
```

### 2. TFLite float32 (Full Precision)
```
Format: Single .tflite file
Size: ~32% reduction (45MB from 140MB)
Inference: 50-100ms on CPU
Accuracy: 100% (no loss)
Use: Fast prototyping
```

### 3. TFLite float16 (Half Precision)
```
Format: Single .tflite file
Size: ~40% reduction (52MB from 140MB)
Inference: 40-80ms on CPU
Accuracy: 99%+ (minimal loss)
Use: Mobile phones, tablets
```

### 4. TFLite int8 (Quantized)
```
Format: Single .tflite file
Size: ~91% reduction (12MB from 140MB)
Inference: 20-50ms on CPU
Accuracy: 97-98% (small loss)
Use: Edge devices, IoT
```

**Comparison:**

| Format | Size | Speed | Accuracy | Best For |
|--------|------|-------|----------|----------|
| SavedModel | 95% | Fast | 100% | Development |
| TFLite float32 | 32% | Fast | 100% | Mobile |
| TFLite float16 | 40% | Faster | 99%+ | Mobile |
| TFLite int8 | 91%! | Fastest | 97-98% | Edge/IoT ⭐ |

## 🔧 Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Export Your Model
```bash
# From Assignment 15, 19, or your trained model
python app.py --model ../Assignment_15/fruit_classifier.h5 --export-all
```

### Step 3: Test Inference
```bash
python app.py \
  --model ../Assignment_15/fruit_classifier.h5 \
  --export-all \
  --test-image test_fruit.jpg
```

### Step 4: Batch Test
```bash
python app.py \
  --model ../Assignment_15/fruit_classifier.h5 \
  --test-dir ./test_images/
```

### Step 5: Deploy to Edge
```bash
# Copy exported_models/ to Raspberry Pi
scp -r exported_models/ pi@raspberrypi.local:/home/pi/fruit_detector/

# On Raspberry Pi:
ssh pi@raspberrypi.local
cd /home/pi/fruit_detector
python edge_runtime.py
```

## 📊 Model Compression Results

### Example: Fruit Detector Export

```
Original Keras Model
├── Size: 140MB
├── Layers: 125
└── Parameters: 3.2M

Exported Formats
├── SavedModel
│   ├── Size: 135MB (96%)
│   └── Inference: 85ms
├── TFLite (float32)
│   ├── Size: 45MB (32%)
│   └── Inference: 75ms
├── TFLite (float16)
│   ├── Size: 52MB (37%)
│   └── Inference: 65ms
└── TFLite (int8)  ⭐ RECOMMENDED FOR EDGE
    ├── Size: 12MB (9%)
    ├── Inference: 35ms
    └── Accuracy Loss: <1%
```

## 💾 File Operations

### Export Model
```python
from app import EdgeModelExporter

exporter = EdgeModelExporter(
    model_path='fruit_classifier.h5',
    model_name='fruit_detector'
)

# Export all formats
exports = exporter.export_all_formats()
# Creates: exported_models/
#   ├── fruit_detector_savedmodel/
#   ├── fruit_detector_float32.tflite
#   ├── fruit_detector_float16.tflite
#   └── fruit_detector_int8.tflite
```

### Run Inference
```python
from app import EdgeInference

inference = EdgeInference(
    'exported_models/fruit_detector_int8.tflite',
    class_names=['ripe', 'unripe', 'overripe', 'unknown']
)

result = inference.predict('apple.jpg')
# Returns:
# {
#   'class': 'ripe',
#   'confidence': 0.95,
#   'inference_time_ms': 35.2,
#   'all_scores': {...}
# }
```

## 🏃 Performance on Edge Device

### Raspberry Pi 4 (4GB RAM, CPU only)

```
Model                 Inference Time    FPS      Memory
────────────────────────────────────────────────────────
TFLite int8           35-45ms           22-28    ~50MB
TFLite float16        50-70ms           14-20    ~80MB
TFLite float32        75-100ms          10-13    ~100MB
SavedModel            150-200ms         5-7      ~200MB
```

**Result: TFLite int8 achieves 22 FPS - good for real-time!**

### NVIDIA Jetson Nano (4GB RAM, GPU)

```
Model                 Inference Time    FPS      Memory
────────────────────────────────────────────────────────
TFLite int8           15-20ms           50-67    ~40MB
TFLite float16        20-30ms           33-50    ~60MB
TFLite float32        25-40ms           25-40    ~80MB
SavedModel            40-60ms           16-25    ~150MB
```

**Result: TFLite int8 on GPU achieves 50+ FPS - excellent!**

## 🔌 Deployment Architecture

### Option A: Direct Inference (Lightweight)
```
Raspberry Pi
├── TFLite Model (12MB)
├── Image Capture
├── Preprocessing
└── Inference Engine → LED Control
```

### Option B: With Cloud Sync
```
Raspberry Pi                     Azure Cloud
├── TFLite Model (12MB)         ├── IoT Hub
├── Image Capture         →      ├── Storage
├── Preprocessing              └── Analytics
├── Inference Engine
├── Result Storage
└── Send Alert
```

## 📝 Hardware Setup

### Minimum Requirements
- **CPU**: ARMv7 or better (Pi Zero to Pi 4)
- **RAM**: 256MB minimum (1GB recommended)
- **Storage**: 50MB for model + OS
- **OS**: Raspberry Pi OS, Ubuntu on ARM, etc.

### Recommended Setup
- **Raspberry Pi 4**: 2GB RAM minimum
- **Jetson Nano**: 4GB RAM (built-in GPU)
- **Storage**: 32GB SD card
- **Power**: 2.5A@ 5V (Pi), 5A@5V (Jetson)

## ✅ Deployment Checklist

- [ ] Model exported in all formats
- [ ] TFLite int8 model tested on development machine
- [ ] Model size verified (<15MB for edge)
- [ ] Inference latency measured (<100ms on edge)
- [ ] Accuracy verified (>90% on edge)
- [ ] Edge device configured and updated
- [ ] Model copied to edge device
- [ ] Edge runtime script working
- [ ] Image preprocessing tested
- [ ] Inference pipeline validated
- [ ] Performance benchmarked
- [ ] Integration with sensors/LEDs working

## 🎓 Exemplary Implementation

### Exemplary Tier Requires:
✅ **Use correct compact domain**
  - Best performing model from Assignment 19
  - Usually EfficientNetB0 or MobileNetV2

✅ **Export as compact model**
  - TFLite int8 format
  - <15MB file size
  - <100ms inference

✅ **Run on edge**
  - Deployed to Raspberry Pi or Jetson
  - Inference working
  - Can classify images in real-time

✅ **Access from IoT device**
  - Can send predictions back
  - Integration with sensors/LEDs
  - Real-world demonstration

## 🧪 Testing on PC vs Edge

### PC Testing (Before Deployment)
```bash
# Verify model works
python app.py --model fruit.h5 --test-image apple.jpg

# Check inference speed
python app.py --model fruit.h5 --test-dir ./images/
```

### Edge Testing (On Device)
```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Test inference
cd /home/pi/fruit_detector
python3 -c "
from edge_runtime import EdgeInferenceServer
server = EdgeInferenceServer('fruit_detector_int8.tflite')
result = server.infer('test.jpg')
print(f'FPS: {1000/result[\"inference_time_ms\"]:.1f}')
"
```

## 📊 Performance Metrics to Track

### Latency
- **Preprocessing**: Image loading, resizing, normalization
- **Inference**: Model computation time
- **Total**: Preprocessing + Inference

### Throughput
- **FPS**: Frames per second
- **Max images/second**: At 90% accuracy threshold

### Resource Usage
- **Memory**: RAM consumed by model + runtime
- **Disk**: Model file size
- **CPU**: Percentage utilization
- **Temperature**: If available on device

### Accuracy
- **On-device**: Verify accuracy matches PC
- **Quantization loss**: Impact of int8 conversion
- **Real-world**: Test with actual camera input

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Model export fails | Check TensorFlow version, use tf 2.13+ |
| TFLite inference errors | Verify input shape matches training |
| Slow on Raspberry Pi | Use int8 quantization, reduce image size |
| "Out of memory" | Reduce batch size, use streaming inference |
| Accuracy drops on edge | Check quantization settings, retrain if needed |
| Cannot SSH to Pi | Check network, verify IP address |

## 📚 References

- [TensorFlow Lite Guide](https://www.tensorflow.org/lite/guide)
- [Model Optimization](https://www.tensorflow.org/lite/performance/post_training_quantization)
- [Deploy to Pi](https://www.tensorflow.org/lite/guide/python)
- [Jetson Nano Setup](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit)

## 🎯 Next Steps

1. **Export your model** from Assignment 15 or 19
2. **Test on PC** with various quantization levels
3. **Choose best format** (usually int8)
4. **Deploy to edge device**
5. **Benchmark performance**
6. **Integrate with sensors** (cameras, LEDs)
7. **Document results**

---

**Remember:** Model optimization is about finding the right balance between accuracy, speed, and size for your specific deployment scenario!
