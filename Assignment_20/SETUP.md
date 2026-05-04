# Setup & Installation Guide - Assignment 20

## Prerequisites

- Python 3.7+ (3.9+ recommended)
- TensorFlow 2.13+
- 500MB free disk space
- 2GB RAM (for export process)

## Installation

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

Installs:
- TensorFlow 2.13
- NumPy 1.24
- Pillow 10.0
- OpenCV 4.8

### 3. Verify Installation

```bash
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} OK')"
python -c "import numpy; print(f'NumPy {numpy.__version__} OK')"
python -c "import PIL; print('PIL OK')"
```

## Before You Start

### Get a Trained Model

You need a Keras model (.h5 file) from:
- Assignment 15 (fruit_classifier.h5)
- Assignment 19 (any domain model)
- Your own trained model

```bash
# Example: locate existing model
find .. -name "*.h5" -type f
```

## Quick Test

```bash
# 1. Create test directory
mkdir test_images

# 2. Copy some images (or use synthetic)
cp ../Assignment_15/test_images/* test_images/  # If available

# 3. Export model
python app.py --model ../Assignment_15/fruit_classifier.h5 --export-all

# 4. Test inference
python app.py --model ../Assignment_15/fruit_classifier.h5 --test-dir test_images/
```

## File Organization

```
Assignment_20/
├── app.py                 # Main export/inference code
├── edge_runtime.py        # Edge device runtime
├── requirements.txt
├── SETUP.md              # This file
├── README.md
├── assignment20.md
└── exported_models/       # Created after running app.py
    ├── fruit_detector_savedmodel/
    ├── fruit_detector_float32.tflite
    ├── fruit_detector_float16.tflite
    └── fruit_detector_int8.tflite
```

## Troubleshooting Installation

### Error: ModuleNotFoundError: No module named 'tensorflow'

```bash
# Reinstall TensorFlow
pip install --upgrade tensorflow==2.13.0
```

### Error: "Could not load dynamic library"

On Ubuntu/Raspberry Pi:
```bash
sudo apt-get install libatlas-base-dev libjasper-dev libtiff5 libjasper1
```

### Error: Out of memory during export

Reduce TensorFlow verbosity:
```bash
export TF_CPP_MIN_LOG_LEVEL=3
python app.py --model fruit.h5 --export-all
```

## Next Steps

1. Verify installation works
2. Read README.md for quick start
3. See assignment20.md for detailed guide
4. Export your model
5. Test on PC
6. Deploy to edge device

## Support

- **assignment20.md**: Full technical documentation
- **README.md**: Quick reference and commands
- **edge_runtime.py**: Edge device deployment code
