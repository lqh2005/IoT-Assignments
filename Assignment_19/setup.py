#!/usr/bin/env python3
"""
Quick comparison test for domain performance.
Runs a lightweight comparison without training.
"""

import os
import sys
import json
from pathlib import Path

def test_imports():
    """Test if all required packages are installed."""
    print("Testing imports...")
    
    packages = [
        'tensorflow',
        'keras',
        'numpy',
        'cv2',
        'matplotlib',
        'PIL'
    ]
    
    missing = []
    for package in packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    return len(missing) == 0

def create_sample_data():
    """Create sample fruit data structure."""
    print("\nCreating sample data directory structure...")
    
    base_dir = Path('./fruit_data')
    splits = ['train', 'validation', 'test']
    fruits = ['apple', 'banana', 'orange', 'tomato']
    
    for split in splits:
        for fruit in fruits:
            fruit_dir = base_dir / split / fruit
            fruit_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"  Created: {base_dir}")
    print(f"  Splits: {splits}")
    print(f"  Classes: {fruits}")
    print("\n  ⚠️  Now add your image files to each directory:")
    print(f"     {base_dir}/train/apple/ - add 100+ apple images")
    print(f"     {base_dir}/train/banana/ - add 100+ banana images")
    print(f"     etc...")

def show_domains():
    """Display available domains."""
    print("\nAvailable Domains for Comparison:\n")
    
    domains = {
        'mobilenetv2': {
            'size_mb': 140,
            'input_size': '224×224',
            'inference': 'Fast (50-100ms)',
            'best_for': 'Mobile devices'
        },
        'resnet50': {
            'size_mb': 102,
            'input_size': '224×224',
            'inference': 'Medium (100-200ms)',
            'best_for': 'Balanced accuracy/speed'
        },
        'inceptionv3': {
            'size_mb': 92,
            'input_size': '299×299',
            'inference': 'Slow (200-300ms)',
            'best_for': 'Maximum accuracy'
        },
        'efficientnetb0': {
            'size_mb': 29,
            'input_size': '224×224',
            'inference': 'Very Fast (50ms)',
            'best_for': 'Edge devices ⭐'
        },
        'vgg16': {
            'size_mb': 138,
            'input_size': '224×224',
            'inference': 'Slow (300-400ms)',
            'best_for': 'Research/learning'
        }
    }
    
    for domain, info in domains.items():
        print(f"  {domain.upper()}")
        print(f"    Size: {info['size_mb']}MB")
        print(f"    Input: {info['input_size']}")
        print(f"    Speed: {info['inference']}")
        print(f"    Use: {info['best_for']}\n")

def main():
    """Run setup checks."""
    print("="*60)
    print("ASSIGNMENT 19 - DOMAIN COMPARISON SETUP")
    print("="*60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Missing packages! Install with:")
        print("   pip install -r requirements.txt")
        return 1
    
    print("\n✅ All packages installed successfully!")
    
    # Show domains
    show_domains()
    
    # Create sample data
    create_sample_data()
    
    # Next steps
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("""
1. Add your image files to fruit_data/ directories
   - At least 50 images per class per split
   - RGB images (JPG, PNG)
   
2. Train and compare all domains:
   python app.py --epochs 10 --plot
   
3. Compare specific domains:
   python app.py --domains mobilenetv2 efficientnetb0 --epochs 5 --plot
   
4. View results:
   - comparison_results.json (metrics)
   - domain_comparison.png (plots)
   
5. Read assignment19.md for detailed analysis
""")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
