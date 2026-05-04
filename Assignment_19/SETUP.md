# Setup Guide - Assignment 19

## Prerequisites

- Python 3.9 or higher
- 2GB+ RAM (more for training multiple domains)
- 500MB free disk space (for models)
- GPU (optional, but recommended for faster training)

## Installation Steps

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- TensorFlow 2.13 (with Keras)
- NumPy 1.24
- Matplotlib 3.7
- OpenCV 4.8
- Pillow 10.0
- scikit-learn 1.3

### 3. Verify Installation

```bash
python setup.py
```

Expected output:
```
✓ tensorflow
✓ keras
✓ numpy
✓ cv2
✓ matplotlib
✓ PIL

✅ All packages installed successfully!
```

### 4. Prepare Data

Create directory structure:
```
fruit_data/
├── train/
│   ├── apple/ (100+ images)
│   ├── banana/ (100+ images)
│   ├── orange/ (100+ images)
│   └── tomato/ (100+ images)
├── validation/
│   ├── apple/ (20-30 images)
│   ├── banana/ (20-30 images)
│   ├── orange/ (20-30 images)
│   └── tomato/ (20-30 images)
└── test/
    ├── apple/ (20-30 images)
    ├── banana/ (20-30 images)
    ├── orange/ (20-30 images)
    └── tomato/ (20-30 images)
```

Or automatically:
```bash
python -c "from setup import create_sample_data; create_sample_data()"
```

## Quick Start

### Option A: Compare All 5 Domains

```bash
python app.py --epochs 10 --plot
```

This will:
1. Train MobileNetV2 (10 epochs)
2. Train ResNet50 (10 epochs)
3. Train InceptionV3 (10 epochs)
4. Train EfficientNetB0 (10 epochs)
5. Train VGG16 (10 epochs)
6. Generate comparison report
7. Save plots to domain_comparison.png

**Estimated time:** 20-40 minutes (depends on GPU/CPU)

### Option B: Compare Specific Domains (Faster)

```bash
# Compare fastest 2 domains
python app.py --epochs 5 --domains efficientnetb0 mobilenetv2 --plot

# Estimated time: 5-10 minutes
```

### Option C: Train Single Domain

```bash
# Train EfficientNetB0 only (best overall)
python app.py --epochs 15 --domains efficientnetb0 --plot

# Estimated time: 3-5 minutes
```

## Understanding the Output

### Console Output

```
============================================================
COMPARING ALL DOMAINS
============================================================

>>> Processing domain: mobilenetv2
Building model with domain: mobilenetv2
  Input size: (224, 224)
  Model size: 140MB
  Base model frozen (transfer learning)
Model built successfully

Epoch 1/10
20/20 [==============================] - 15s 750ms/step
...
Epoch 10/10
20/20 [==============================] - 14s 700ms/step

Training complete:
  Training accuracy: 0.9234
  Validation accuracy: 0.8956
  Training time: 150.23s
  Model saved: ./models/mobilenetv2_model.h5

Evaluating mobilenetv2...
  Test accuracy: 0.8912
  Test loss: 0.3456
  Avg inference time: 52.34ms/batch

>>> Processing domain: resnet50
...
```

### Comparison Report

```
====================================================
DOMAIN COMPARISON REPORT
====================================================

Domain                Accuracy         Loss       Inference(ms)   Size(MB)
---------------------------------------------------------------------------
efficientnetb0           0.9650       0.1234            45.23        29
mobilenetv2              0.9540       0.1456            52.34       140
resnet50                 0.9480       0.1678           125.67       102
inceptionv3              0.9420       0.1890           215.43        92
vgg16                    0.9310       0.2145           340.21       138

✅ BEST DOMAIN: efficientnetb0
   Accuracy: 0.9650
   Reason: Highest accuracy for fruit classification
```

### Generated Files

```
models/
├── mobilenetv2_model.h5    (140MB)
├── resnet50_model.h5       (102MB)
├── inceptionv3_model.h5    (92MB)
├── efficientnetb0_model.h5 (29MB)
└── vgg16_model.h5          (138MB)

comparison_results.json     (Detailed metrics)
domain_comparison.png       (4 comparison plots)
```

## Troubleshooting

### Issue: OutOfMemory Error

**Solution:** Use fewer domains or reduce batch size
```bash
# Train one domain at a time
python app.py --epochs 5 --domains efficientnetb0

# Edit app.py: reduce batch_size from 32 to 16
```

### Issue: Data Loading Error

**Solution:** Verify data structure
```bash
# Check if directories exist
ls -la fruit_data/train/apple/
# Should show image files (.jpg, .png)
```

### Issue: TensorFlow GPU Not Found

**Solution:** TensorFlow will fall back to CPU (slower but works)
```bash
# For GPU support, install CUDA/cuDNN separately
# See: https://www.tensorflow.org/install/source#tested_build_configurations
```

### Issue: Import Error

**Solution:** Reinstall packages
```bash
pip install --upgrade -r requirements.txt
```

## Performance Tuning

### For Faster Training

```bash
# Reduce epochs
python app.py --epochs 3 --domains efficientnetb0

# Or reduce training data size (subsample)
```

### For Better Accuracy

```bash
# Train longer
python app.py --epochs 20 --domains inceptionv3

# Or fine-tune (unfreeze base model)
# Modify app.py: freeze_base=False
```

### For Multiple GPUs

```bash
# Modify app.py to use multiple GPUs
# See TensorFlow distributed training docs
```

## File Structure

```
Assignment_19/
├── app.py                 # Main domain comparator
├── setup.py              # Setup verification
├── requirements.txt      # Python dependencies
├── README.md             # Quick reference
├── SETUP.md              # This file
└── assignment19.md       # Full documentation

# Generated after running:
models/                   # Trained model files
comparison_results.json  # Comparison metrics
domain_comparison.png    # Plots
```

## Next Steps

1. **Run setup verification:** `python setup.py`
2. **Prepare your data:** Add images to fruit_data/
3. **Train models:** `python app.py --epochs 10 --plot`
4. **Analyze results:** View comparison_results.json and plots
5. **Write report:** Document findings in assignment19.md

## Support

- Check **README.md** for quick reference
- Check **assignment19.md** for detailed explanations
- Review domain descriptions to understand trade-offs
