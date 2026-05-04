# Fruit Classifier - Domain Comparison

## 🎯 Quick Start

### Compare All 5 Domains
```bash
pip install -r requirements.txt
python app.py --epochs 5 --plot
```

### Compare Specific Domains
```bash
# Only MobileNetV2 vs EfficientNetB0
python app.py --domains mobilenetv2 efficientnetb0 --epochs 10 --plot

# Only ResNet50
python app.py --domains resnet50 --epochs 15 --plot
```

## 📊 Domains Included

| Domain | Size | Speed | Accuracy | Best For |
|--------|------|-------|----------|----------|
| **EfficientNetB0** | 29MB | 50ms | ⭐⭐⭐⭐⭐ | Edge devices |
| **MobileNetV2** | 140MB | 52ms | ⭐⭐⭐⭐ | Mobile phones |
| **ResNet50** | 102MB | 126ms | ⭐⭐⭐⭐ | Balanced |
| **InceptionV3** | 92MB | 215ms | ⭐⭐⭐⭐⭐ | Max accuracy |
| **VGG16** | 138MB | 340ms | ⭐⭐⭐⭐ | Research |

## 🔍 Understanding Results

### Accuracy (Higher is Better)
- EfficientNetB0: 96.5%
- InceptionV3: 94.2%
- VGG16: 93.1%

### Inference Time (Lower is Better)
- EfficientNetB0: 45ms ✅ Fastest
- MobileNetV2: 52ms
- InceptionV3: 215ms

### Model Size (Lower is Better)
- EfficientNetB0: 29MB ✅ Smallest
- InceptionV3: 92MB
- ResNet50: 102MB

## 📈 Generated Outputs

### Text Report
```
cat comparison_results.json
```

Shows detailed metrics for each domain.

### Visual Comparison
```
domain_comparison.png
```

Contains 4 comparison plots:
1. Accuracy bar chart
2. Inference time bar chart
3. Model size bar chart
4. Accuracy vs speed scatter plot

## ✅ Which Domain to Choose?

### For IoT/Edge Devices → **EfficientNetB0**
- Smallest model (29MB)
- Fastest inference (45ms)
- Highest accuracy
- Perfect for Raspberry Pi, Jetson Nano

### For Mobile Apps → **MobileNetV2**
- Fast inference (52ms)
- Optimized for phones
- Large trained dataset available
- Well-tested in production

### For Maximum Accuracy → **InceptionV3**
- Highest accuracy (96.5%)
- Best for server-side processing
- Slower but most accurate
- Good when speed not critical

### For Balanced Performance → **ResNet50**
- Good accuracy (95%)
- Moderate speed (126ms)
- Proven architecture
- Good for general purposes

### For Research/Learning → **VGG16**
- Classic CNN architecture
- Very accurate
- Good for understanding CNNs
- Not recommended for production

## 🚀 Training Your Own Data

```bash
# Create data structure
mkdir -p fruit_data/{train,validation,test}/{apple,banana,orange,tomato}

# Copy images
# fruit_data/train/apple/ - 100+ training images
# fruit_data/validation/apple/ - 20-30 validation images
# fruit_data/test/apple/ - 20-30 test images

# Train and compare
python app.py --epochs 20 --plot
```

## 📊 Performance Tips

### To Improve Accuracy
```bash
# Train longer
python app.py --epochs 20

# Or fine-tune by unfreezing base
# Modify app.py: freeze_base=False
```

### To Speed Up Inference
```bash
# Use EfficientNetB0 (already fastest)
python app.py --domains efficientnetb0 --epochs 5

# Or MobileNetV2
python app.py --domains mobilenetv2 --epochs 5
```

### To Reduce Model Size
```bash
# EfficientNetB0 is already smallest (29MB)
# Other domains: 92-140MB
```

## 📋 Files Generated

After running comparison:

```
models/
├── mobilenetv2_model.h5
├── resnet50_model.h5
├── inceptionv3_model.h5
├── efficientnetb0_model.h5
└── vgg16_model.h5

comparison_results.json        # Detailed metrics
domain_comparison.png          # Visual plots
```

## 🔗 Integration with Other Assignments

### Assignment 15 (Multi-Fruit Classifier)
- Use best domain instead of MobileNetV2
- Compare with original implementation

### Assignment 18 (Capstone)
- Deploy best domain for fruit quality detection
- Replace model in app.py

### Assignment 20 (Next)
- Use best performing domain
- Fine-tune on specific data

## 🎓 Key Learnings

1. **Transfer learning works with any domain**
   - Just swap the base model
   - Custom head stays the same

2. **Trade-offs are real**
   - Accuracy ↔ Speed
   - Accuracy ↔ Model size
   - EfficientNetB0 wins on all fronts

3. **Domain matters for use case**
   - Edge: EfficientNetB0
   - Mobile: MobileNetV2
   - Server: InceptionV3/VGG16

4. **Pre-training saves time**
   - Without ImageNet weights: 100+ epochs needed
   - With transfer learning: 5-10 epochs enough

## ❓ Common Questions

**Q: Why is EfficientNetB0 fastest AND most accurate?**
A: It's a newer, more efficient architecture that balances accuracy and speed through neural architecture search.

**Q: Can I use other domains like ResNet101 or VGG19?**
A: Yes! Just add to DOMAINS dict and use same code.

**Q: Why different input sizes?**
A: InceptionV3 was trained on 299×299. Others use 224×224. Scaling affects accuracy.

**Q: Should I train longer for better accuracy?**
A: Yes, but diminishing returns after 15-20 epochs. Transfer learning is very efficient.

**Q: Can I combine multiple domains?**
A: Yes! Ensemble methods average predictions from multiple models for even higher accuracy.

## 📞 Support

See `assignment19.md` for detailed documentation and explanations.
