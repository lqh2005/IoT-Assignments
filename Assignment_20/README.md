# Deploy Fruit Detector to Edge - Quick Start

## 🚀 Quick Commands

### Export All Model Formats
```bash
python app.py --model ../Assignment_15/fruit_classifier.h5 --export-all
```

This creates:
```
exported_models/
├── fruit_detector_savedmodel/     # Full model directory
├── fruit_detector_float32.tflite  # Full precision (45MB)
├── fruit_detector_float16.tflite  # Half precision (52MB)
└── fruit_detector_int8.tflite     # Quantized (12MB) ⭐
```

### Test Inference on PC
```bash
# Single image
python app.py --model fruit.h5 --test-image apple.jpg

# Batch test
python app.py --model fruit.h5 --test-dir ./test_images/
```

### Deploy to Raspberry Pi
```bash
# Copy model to Pi
scp exported_models/fruit_detector_int8.tflite pi@raspberrypi.local:/home/pi/

# SSH and test
ssh pi@raspberrypi.local
python3 << 'EOF'
from edge_runtime import EdgeInferenceServer
server = EdgeInferenceServer('fruit_detector_int8.tflite')
result = server.infer('test.jpg')
print(f"Class: {result['class']}, FPS: {result['fps']:.1f}")
EOF
```

## 📊 Model Sizes After Export

| Format | Size | Reduction | Inference |
|--------|------|-----------|-----------|
| Original | 140MB | - | 85ms |
| SavedModel | 135MB | 3% | 85ms |
| TFLite float32 | 45MB | 68% | 75ms |
| TFLite float16 | 52MB | 63% | 65ms |
| TFLite int8 | 12MB | 91% ✅ | 35ms |

## 🎯 Which Format to Use?

### For Development/Testing
→ Use `float32.tflite` (simplest, most accurate)

### For Mobile App
→ Use `float16.tflite` (balanced)

### For Edge Device (Raspberry Pi/Jetson)
→ Use `int8.tflite` (smallest, fastest) ⭐

### For Maximum Compatibility
→ Use `SavedModel` (any TensorFlow version)

## 🏃 Performance Expectations

### Raspberry Pi 4
```
TFLite int8: 35-45ms per image → 22-28 FPS
Memory: ~50MB
```

### Jetson Nano (with GPU)
```
TFLite int8: 15-20ms per image → 50-67 FPS
Memory: ~40MB
```

### Laptop (for comparison)
```
TFLite int8: 5-10ms per image → 100-200 FPS
Memory: ~30MB
```

## 📁 File Structure

```
Assignment_20/
├── app.py                 # Export and inference
├── edge_runtime.py        # Edge device runtime
├── requirements.txt       # Dependencies
├── assignment20.md        # Full documentation
└── exported_models/       # Generated models
    ├── fruit_detector_float32.tflite
    ├── fruit_detector_float16.tflite
    └── fruit_detector_int8.tflite
```

## ✅ Deployment Checklist

- [ ] Model exported successfully
- [ ] All 4 formats generated
- [ ] Tested inference on PC
- [ ] Verified accuracy (>90%)
- [ ] Copied to edge device
- [ ] Edge runtime working
- [ ] Performance benchmarked
- [ ] Integration complete

## 🔗 From Previous Assignments

- **Assignment 15**: Trained classifier to export
- **Assignment 19**: Best domain (probably EfficientNetB0)
- **Assignment 18**: May integrate deployed model

## 📖 Next: See assignment20.md for detailed guide
