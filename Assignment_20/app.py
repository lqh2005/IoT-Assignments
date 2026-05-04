"""
Assignment 20: Deploy Fruit Detector to Edge
Export compact model and run on edge device (Raspberry Pi, Jetson Nano).
"""

import os
import sys
import time
import json
import numpy as np
import logging
from pathlib import Path
from datetime import datetime

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import load_img, img_to_array

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EdgeModelExporter:
    """
    Export Keras model to TensorFlow Lite for edge deployment.
    Optimizes model for size and speed on resource-constrained devices.
    """
    
    def __init__(self, model_path, model_name='fruit_detector'):
        """
        Initialize exporter.
        
        Args:
            model_path: Path to trained Keras model (.h5)
            model_name: Name for exported models
        """
        self.model_path = Path(model_path)
        self.model_name = model_name
        self.model = None
        self.output_dir = Path('./exported_models')
        self.output_dir.mkdir(exist_ok=True)
        
        self._load_model()
    
    def _load_model(self):
        """Load Keras model from disk."""
        if not self.model_path.exists():
            logger.error(f"Model not found: {self.model_path}")
            return
        
        try:
            self.model = keras.models.load_model(str(self.model_path))
            logger.info(f"Model loaded: {self.model_path}")
            logger.info(f"Model size: {self.model_path.stat().st_size / (1024*1024):.2f}MB")
            
            # Print model info
            self.model.summary()
        
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    def export_keras(self, save_path=None):
        """
        Save model as Keras SavedModel format.
        Best for deployment compatibility.
        """
        if self.model is None:
            logger.error("No model loaded")
            return None
        
        if save_path is None:
            save_path = self.output_dir / f'{self.model_name}_savedmodel'
        
        try:
            self.model.save(str(save_path))
            logger.info(f"SavedModel exported: {save_path}")
            return save_path
        
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return None
    
    def export_tflite(self, quantization='float32', save_path=None):
        """
        Export to TensorFlow Lite format for edge devices.
        
        Args:
            quantization: 'float32' (full precision), 'float16' (half precision),
                         'int8' (quantized)
            save_path: Output path for .tflite file
        
        Returns:
            Path to exported .tflite model
        """
        if self.model is None:
            logger.error("No model loaded")
            return None
        
        if save_path is None:
            quant_suffix = '' if quantization == 'float32' else f'_{quantization}'
            save_path = self.output_dir / f'{self.model_name}{quant_suffix}.tflite'
        
        try:
            logger.info(f"Exporting to TFLite ({quantization})...")
            
            # Create converter
            concrete_func = tf.function(lambda x: self.model(x))
            concrete_func = concrete_func.get_concrete_function(
                tf.TensorSpec(self.model.inputs[0].shape, self.model.inputs[0].dtype)
            )
            
            converter = tf.lite.TFLiteConverter.from_concrete_functions([concrete_func])
            
            # Set optimization based on quantization type
            if quantization == 'float32':
                logger.info("  Format: Full precision (float32)")
            
            elif quantization == 'float16':
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
                converter.target_spec.supported_types = [tf.float16]
                logger.info("  Format: Half precision (float16)")
            
            elif quantization == 'int8':
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
                converter.target_spec.supported_types = [tf.int8]
                logger.info("  Format: Full integer quantization (int8)")
            
            else:
                logger.warning(f"Unknown quantization: {quantization}, using float32")
            
            # Convert
            tflite_model = converter.convert()
            
            # Save
            save_path = Path(save_path)
            with open(save_path, 'wb') as f:
                f.write(tflite_model)
            
            file_size_kb = save_path.stat().st_size / 1024
            logger.info(f"TFLite model exported: {save_path}")
            logger.info(f"  File size: {file_size_kb:.2f}KB")
            
            # Show compression ratio
            original_size = self.model_path.stat().st_size / (1024*1024)
            compressed_size = file_size_kb / 1024
            ratio = (1 - compressed_size / original_size) * 100
            logger.info(f"  Compression: {ratio:.1f}% reduction")
            
            return save_path
        
        except Exception as e:
            logger.error(f"TFLite export failed: {e}")
            return None
    
    def export_all_formats(self):
        """Export model in all optimized formats."""
        logger.info("\n" + "="*60)
        logger.info("EXPORTING MODEL IN MULTIPLE FORMATS")
        logger.info("="*60 + "\n")
        
        exports = {}
        
        # SavedModel
        exports['savedmodel'] = self.export_keras()
        
        # TFLite formats
        exports['tflite_float32'] = self.export_tflite('float32')
        exports['tflite_float16'] = self.export_tflite('float16')
        exports['tflite_int8'] = self.export_tflite('int8')
        
        logger.info("\n" + "="*60)
        logger.info("EXPORT SUMMARY")
        logger.info("="*60)
        
        for fmt, path in exports.items():
            if path:
                size = path.stat().st_size
                if size > 1024*1024:
                    size_str = f"{size / (1024*1024):.2f}MB"
                elif size > 1024:
                    size_str = f"{size / 1024:.2f}KB"
                else:
                    size_str = f"{size}B"
                
                logger.info(f"✓ {fmt:<25} {size_str:>10}")
        
        return exports
    
    def get_model_info(self):
        """Get detailed model information."""
        if self.model is None:
            return None
        
        info = {
            'name': self.model_name,
            'input_shape': tuple(self.model.input_shape),
            'output_shape': tuple(self.model.output_shape),
            'total_params': int(self.model.count_params()),
            'trainable_params': sum([tf.size(w).numpy() for w in self.model.trainable_weights]),
            'non_trainable_params': sum([tf.size(w).numpy() for w in self.model.non_trainable_weights])
        }
        
        return info


class EdgeInference:
    """
    Run inference on edge device using TFLite model.
    Optimized for CPU-bound inference on Raspberry Pi/Jetson.
    """
    
    def __init__(self, tflite_model_path, class_names=None):
        """
        Initialize edge inference engine.
        
        Args:
            tflite_model_path: Path to .tflite model
            class_names: List of class names
        """
        self.model_path = Path(tflite_model_path)
        self.class_names = class_names or ['ripe', 'unripe', 'overripe', 'unknown']
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.inference_times = []
        
        self._load_model()
    
    def _load_model(self):
        """Load TFLite model."""
        if not self.model_path.exists():
            logger.error(f"Model not found: {self.model_path}")
            return
        
        try:
            # Create interpreter
            self.interpreter = tf.lite.Interpreter(str(self.model_path))
            self.interpreter.allocate_tensors()
            
            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            model_size = self.model_path.stat().st_size / 1024
            logger.info(f"TFLite model loaded: {self.model_path}")
            logger.info(f"  Size: {model_size:.2f}KB")
            logger.info(f"  Input shape: {self.input_details[0]['shape']}")
            logger.info(f"  Output shape: {self.output_details[0]['shape']}")
        
        except Exception as e:
            logger.error(f"Failed to load TFLite model: {e}")
    
    def predict(self, image_path):
        """
        Run inference on image.
        
        Args:
            image_path: Path to input image
        
        Returns:
            Dictionary with prediction results
        """
        if self.interpreter is None:
            logger.error("Model not loaded")
            return None
        
        try:
            # Load and preprocess image
            start_time = time.time()
            
            img = load_img(image_path, target_size=(224, 224))
            img_array = img_to_array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            preprocess_time = (time.time() - start_time) * 1000
            
            # Run inference
            inference_start = time.time()
            
            self.interpreter.set_tensor(
                self.input_details[0]['index'],
                img_array.astype(self.input_details[0]['dtype'])
            )
            self.interpreter.invoke()
            
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            inference_time_ms = (time.time() - inference_start) * 1000
            self.inference_times.append(inference_time_ms)
            
            # Parse results
            predictions = output_data[0]
            class_idx = np.argmax(predictions)
            confidence = float(predictions[class_idx])
            
            result = {
                'class': self.class_names[class_idx] if class_idx < len(self.class_names) else 'unknown',
                'class_index': int(class_idx),
                'confidence': float(confidence),
                'inference_time_ms': inference_time_ms,
                'preprocess_time_ms': preprocess_time,
                'all_scores': {self.class_names[i]: float(predictions[i]) 
                             for i in range(len(self.class_names))}
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return None
    
    def batch_predict(self, image_dir, pattern='*.jpg'):
        """
        Run inference on multiple images.
        
        Args:
            image_dir: Directory containing images
            pattern: File pattern (e.g., '*.jpg')
        
        Returns:
            List of results
        """
        image_dir = Path(image_dir)
        images = list(image_dir.glob(pattern))
        
        logger.info(f"Running batch inference on {len(images)} images...")
        
        results = []
        for i, image_path in enumerate(images):
            result = self.predict(str(image_path))
            if result:
                result['image'] = str(image_path)
                results.append(result)
            
            if (i + 1) % 10 == 0:
                logger.info(f"  Processed {i + 1}/{len(images)}")
        
        return results
    
    def get_statistics(self):
        """Get inference statistics."""
        if not self.inference_times:
            return None
        
        times = np.array(self.inference_times)
        
        return {
            'total_inferences': len(times),
            'avg_time_ms': float(np.mean(times)),
            'min_time_ms': float(np.min(times)),
            'max_time_ms': float(np.max(times)),
            'std_dev_ms': float(np.std(times)),
            'fps': float(1000 / np.mean(times))
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy fruit detector to edge')
    parser.add_argument('--model', type=str, required=True, help='Path to Keras model')
    parser.add_argument('--name', type=str, default='fruit_detector', help='Model name')
    parser.add_argument('--export-all', action='store_true', help='Export all formats')
    parser.add_argument('--test-image', type=str, help='Test image path')
    parser.add_argument('--test-dir', type=str, help='Test directory')
    
    args = parser.parse_args()
    
    # Export model
    exporter = EdgeModelExporter(args.model, args.name)
    
    if args.export_all:
        exports = exporter.export_all_formats()
        
        # Use first available model for testing
        tflite_models = [v for k, v in exports.items() if k.startswith('tflite')]
        if not tflite_models:
            logger.error("No TFLite models exported")
            return
        
        best_tflite = tflite_models[0]
    else:
        best_tflite = exporter.export_tflite('int8')
    
    # Test inference
    if args.test_image:
        logger.info("\n" + "="*60)
        logger.info("TESTING EDGE INFERENCE")
        logger.info("="*60)
        
        inference_engine = EdgeInference(str(best_tflite))
        result = inference_engine.predict(args.test_image)
        
        if result:
            logger.info(f"\nPrediction: {result['class']}")
            logger.info(f"Confidence: {result['confidence']:.4f}")
            logger.info(f"Inference time: {result['inference_time_ms']:.2f}ms")
    
    if args.test_dir:
        logger.info("\n" + "="*60)
        logger.info("BATCH INFERENCE TEST")
        logger.info("="*60)
        
        inference_engine = EdgeInference(str(best_tflite))
        results = inference_engine.batch_predict(args.test_dir)
        
        if results:
            stats = inference_engine.get_statistics()
            logger.info(f"\nStatistics:")
            logger.info(f"  Total: {stats['total_inferences']} inferences")
            logger.info(f"  Average: {stats['avg_time_ms']:.2f}ms")
            logger.info(f"  FPS: {stats['fps']:.2f}")


if __name__ == '__main__':
    main()
