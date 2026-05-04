"""
Assignment 19: Compare Domains for Fruit Classification
Tests multiple pre-trained models to find which works best for fruit classification.
"""

import os
import sys
import time
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import logging

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import (
    MobileNetV2, ResNet50, InceptionV3, EfficientNetB0, VGG16
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DomainComparator:
    """
    Compare multiple pre-trained models (domains) for fruit classification.
    
    Supported domains:
    - MobileNetV2: Fast inference, mobile-friendly (140MB)
    - ResNet50: Accurate, moderate size (102MB)
    - InceptionV3: Very accurate, larger (92MB)
    - EfficientNetB0: State-of-art, efficient (29MB)
    - VGG16: Classic, larger (138MB)
    """
    
    DOMAINS = {
        'mobilenetv2': {
            'model_class': MobileNetV2,
            'input_size': (224, 224),
            'model_size_mb': 140,
            'inference_speed': 'Fast',
            'description': 'MobileNetV2: Optimized for mobile/edge devices'
        },
        'resnet50': {
            'model_class': ResNet50,
            'input_size': (224, 224),
            'model_size_mb': 102,
            'inference_speed': 'Medium',
            'description': 'ResNet50: Balanced accuracy and speed'
        },
        'inceptionv3': {
            'model_class': InceptionV3,
            'input_size': (299, 299),
            'model_size_mb': 92,
            'inference_speed': 'Slow',
            'description': 'InceptionV3: High accuracy'
        },
        'efficientnetb0': {
            'model_class': EfficientNetB0,
            'input_size': (224, 224),
            'model_size_mb': 29,
            'inference_speed': 'Very Fast',
            'description': 'EfficientNetB0: Best accuracy/efficiency'
        },
        'vgg16': {
            'model_class': VGG16,
            'input_size': (224, 224),
            'model_size_mb': 138,
            'inference_speed': 'Slow',
            'description': 'VGG16: Classic CNN architecture'
        }
    }
    
    def __init__(self, num_classes=4, data_dir='./fruit_data'):
        """Initialize domain comparator."""
        self.num_classes = num_classes
        self.data_dir = Path(data_dir)
        self.results = {}
        self.models = {}
        self.histories = {}
        
        logger.info("DomainComparator initialized")
        logger.info(f"Available domains: {', '.join(self.DOMAINS.keys())}")
    
    def build_model(self, domain_name, freeze_base=True):
        """
        Build transfer learning model with specified domain.
        
        Args:
            domain_name: Name of pre-trained model domain
            freeze_base: If True, freeze base model weights
        
        Returns:
            keras.Model
        """
        if domain_name not in self.DOMAINS:
            raise ValueError(f"Unknown domain: {domain_name}")
        
        domain_info = self.DOMAINS[domain_name]
        input_size = domain_info['input_size']
        
        logger.info(f"Building model with domain: {domain_name}")
        logger.info(f"  Input size: {input_size}")
        logger.info(f"  Model size: {domain_info['model_size_mb']}MB")
        
        # Load pre-trained base model
        base_model = domain_info['model_class'](
            input_shape=(*input_size, 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model weights
        if freeze_base:
            base_model.trainable = False
            logger.info("  Base model frozen (transfer learning)")
        else:
            logger.info("  Base model trainable (fine-tuning)")
        
        # Add custom classification head
        model = keras.Sequential([
            layers.Input(shape=(*input_size, 3)),
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info(f"Model built successfully")
        return model
    
    def prepare_data(self, domain_name):
        """
        Prepare data generators for specific domain input size.
        
        Args:
            domain_name: Domain name (determines input size)
        
        Returns:
            (train_generator, validation_generator)
        """
        input_size = self.DOMAINS[domain_name]['input_size']
        
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            zoom_range=0.2,
            horizontal_flip=True,
            shear_range=0.2,
            fill_mode='nearest'
        )
        
        val_datagen = ImageDataGenerator(rescale=1./255)
        
        # Load training data
        train_generator = train_datagen.flow_from_directory(
            self.data_dir / 'train',
            target_size=input_size,
            batch_size=32,
            class_mode='categorical'
        )
        
        # Load validation data
        validation_generator = val_datagen.flow_from_directory(
            self.data_dir / 'validation',
            target_size=input_size,
            batch_size=32,
            class_mode='categorical'
        )
        
        return train_generator, validation_generator
    
    def train_domain(self, domain_name, epochs=10, data_dir=None):
        """
        Train model with specified domain.
        
        Args:
            domain_name: Domain to train
            epochs: Number of training epochs
            data_dir: Data directory (uses self.data_dir if None)
        
        Returns:
            history
        """
        if data_dir:
            self.data_dir = Path(data_dir)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Training domain: {domain_name}")
        logger.info(f"{'='*60}")
        
        # Build model
        model = self.build_model(domain_name, freeze_base=True)
        
        # Prepare data
        try:
            train_gen, val_gen = self.prepare_data(domain_name)
        except Exception as e:
            logger.error(f"Data loading error: {e}")
            return None
        
        # Train model
        start_time = time.time()
        
        history = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=epochs,
            verbose=1
        )
        
        training_time = time.time() - start_time
        
        # Store model and history
        self.models[domain_name] = model
        self.histories[domain_name] = history.history
        
        # Calculate metrics
        final_acc = history.history['accuracy'][-1]
        final_val_acc = history.history['val_accuracy'][-1]
        
        logger.info(f"\nTraining complete:")
        logger.info(f"  Training accuracy: {final_acc:.4f}")
        logger.info(f"  Validation accuracy: {final_val_acc:.4f}")
        logger.info(f"  Training time: {training_time:.2f}s")
        
        # Save model
        model_path = Path('./models') / f'{domain_name}_model.h5'
        model_path.parent.mkdir(exist_ok=True)
        model.save(str(model_path))
        logger.info(f"  Model saved: {model_path}")
        
        return history
    
    def evaluate_domain(self, domain_name, test_dir=None):
        """
        Evaluate trained model on test data.
        
        Args:
            domain_name: Domain to evaluate
            test_dir: Test data directory
        
        Returns:
            (test_loss, test_accuracy, inference_time)
        """
        if domain_name not in self.models:
            logger.error(f"Model not trained: {domain_name}")
            return None
        
        model = self.models[domain_name]
        input_size = self.DOMAINS[domain_name]['input_size']
        
        # Load test data
        test_datagen = ImageDataGenerator(rescale=1./255)
        test_dir = test_dir or (self.data_dir / 'test')
        
        try:
            test_generator = test_datagen.flow_from_directory(
                test_dir,
                target_size=input_size,
                batch_size=32,
                class_mode='categorical'
            )
        except Exception as e:
            logger.warning(f"Test data not found: {e}, using validation data")
            return None
        
        # Evaluate
        logger.info(f"Evaluating {domain_name}...")
        start_time = time.time()
        
        test_loss, test_acc = model.evaluate(test_generator, verbose=0)
        
        inference_time = (time.time() - start_time) / len(test_generator)
        
        logger.info(f"  Test accuracy: {test_acc:.4f}")
        logger.info(f"  Test loss: {test_loss:.4f}")
        logger.info(f"  Avg inference time: {inference_time*1000:.2f}ms/batch")
        
        return {
            'loss': test_loss,
            'accuracy': test_acc,
            'inference_time_ms': inference_time * 1000
        }
    
    def compare_all_domains(self, epochs=5):
        """
        Train and evaluate all domains, generate comparison report.
        
        Args:
            epochs: Epochs to train each model
        
        Returns:
            Comparison results dictionary
        """
        logger.info("\n" + "="*60)
        logger.info("COMPARING ALL DOMAINS")
        logger.info("="*60)
        
        results = {}
        
        for domain_name in self.DOMAINS.keys():
            logger.info(f"\n>>> Processing domain: {domain_name}")
            
            try:
                # Train
                self.train_domain(domain_name, epochs=epochs)
                
                # Evaluate
                eval_result = self.evaluate_domain(domain_name)
                
                if eval_result:
                    domain_info = self.DOMAINS[domain_name]
                    results[domain_name] = {
                        'description': domain_info['description'],
                        'input_size': domain_info['input_size'],
                        'model_size_mb': domain_info['model_size_mb'],
                        'inference_speed': domain_info['inference_speed'],
                        'accuracy': eval_result['accuracy'],
                        'loss': eval_result['loss'],
                        'inference_time_ms': eval_result['inference_time_ms']
                    }
                    
            except Exception as e:
                logger.error(f"Error processing {domain_name}: {e}")
        
        self.results = results
        return results
    
    def generate_comparison_report(self):
        """Generate detailed comparison report."""
        if not self.results:
            logger.warning("No results to report")
            return
        
        logger.info("\n" + "="*60)
        logger.info("DOMAIN COMPARISON REPORT")
        logger.info("="*60)
        
        # Sort by accuracy
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]['accuracy'],
            reverse=True
        )
        
        print("\n{:<20} {:>10} {:>15} {:>15} {:>15}".format(
            "Domain", "Accuracy", "Loss", "Inference(ms)", "Size(MB)"
        ))
        print("-" * 75)
        
        for domain, metrics in sorted_results:
            print("{:<20} {:>10.4f} {:>15.4f} {:>15.2f} {:>15}".format(
                domain,
                metrics['accuracy'],
                metrics['loss'],
                metrics['inference_time_ms'],
                metrics['model_size_mb']
            ))
        
        # Best domain
        best_domain = sorted_results[0][0]
        best_acc = sorted_results[0][1]['accuracy']
        
        logger.info(f"\n✅ BEST DOMAIN: {best_domain}")
        logger.info(f"   Accuracy: {best_acc:.4f}")
        logger.info(f"   Reason: Highest accuracy for fruit classification")
        
        # Analysis
        logger.info("\n📊 ANALYSIS:")
        
        fastest = min(
            self.results.items(),
            key=lambda x: x[1]['inference_time_ms']
        )
        logger.info(f"  Fastest inference: {fastest[0]} ({fastest[1]['inference_time_ms']:.2f}ms)")
        
        smallest = min(
            self.results.items(),
            key=lambda x: x[1]['model_size_mb']
        )
        logger.info(f"  Smallest model: {smallest[0]} ({smallest[1]['model_size_mb']}MB)")
        
        # Detailed descriptions
        logger.info("\n📋 DETAILED ANALYSIS:")
        for domain, metrics in sorted_results:
            logger.info(f"\n{domain.upper()}:")
            logger.info(f"  {metrics['description']}")
            logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
            logger.info(f"  Model size: {metrics['model_size_mb']}MB")
            logger.info(f"  Inference speed: {metrics['inference_speed']}")
            logger.info(f"  Use case: ", end="")
            
            # Recommendation
            if metrics['accuracy'] > 0.92:
                logger.info("Maximum accuracy needed (cloud)")
            elif metrics['inference_time_ms'] < 100:
                logger.info("Real-time edge inference (mobile)")
            else:
                logger.info("Balanced use case")
    
    def plot_comparison(self):
        """Generate comparison plots."""
        if not self.results:
            logger.warning("No results to plot")
            return
        
        domains = list(self.results.keys())
        accuracies = [self.results[d]['accuracy'] for d in domains]
        inference_times = [self.results[d]['inference_time_ms'] for d in domains]
        model_sizes = [self.results[d]['model_size_mb'] for d in domains]
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Accuracy comparison
        axes[0, 0].bar(domains, accuracies, color='green', alpha=0.7)
        axes[0, 0].set_title('Accuracy Comparison')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].set_ylim([0, 1])
        for i, v in enumerate(accuracies):
            axes[0, 0].text(i, v + 0.02, f'{v:.3f}', ha='center')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Inference time comparison
        axes[0, 1].bar(domains, inference_times, color='blue', alpha=0.7)
        axes[0, 1].set_title('Inference Time Comparison')
        axes[0, 1].set_ylabel('Time (ms)')
        for i, v in enumerate(inference_times):
            axes[0, 1].text(i, v + 1, f'{v:.1f}ms', ha='center')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Model size comparison
        axes[1, 0].bar(domains, model_sizes, color='orange', alpha=0.7)
        axes[1, 0].set_title('Model Size Comparison')
        axes[1, 0].set_ylabel('Size (MB)')
        for i, v in enumerate(model_sizes):
            axes[1, 0].text(i, v + 2, f'{v}MB', ha='center')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Accuracy vs Inference time (scatter)
        axes[1, 1].scatter(inference_times, accuracies, s=200, alpha=0.7)
        for i, domain in enumerate(domains):
            axes[1, 1].annotate(domain, (inference_times[i], accuracies[i]),
                              xytext=(5, 5), textcoords='offset points', fontsize=9)
        axes[1, 1].set_title('Accuracy vs Inference Speed')
        axes[1, 1].set_xlabel('Inference Time (ms)')
        axes[1, 1].set_ylabel('Accuracy')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('domain_comparison.png', dpi=150, bbox_inches='tight')
        logger.info("Comparison plot saved: domain_comparison.png")
        plt.show()
    
    def save_results(self, filename='comparison_results.json'):
        """Save comparison results to JSON."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Results saved: {filename}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare fruit classifier domains')
    parser.add_argument('--epochs', type=int, default=5, help='Epochs per domain')
    parser.add_argument('--data-dir', type=str, default='./fruit_data', help='Data directory')
    parser.add_argument('--domains', nargs='+', default=list(DomainComparator.DOMAINS.keys()),
                       help='Domains to compare')
    parser.add_argument('--plot', action='store_true', help='Generate plots')
    
    args = parser.parse_args()
    
    # Initialize comparator
    comparator = DomainComparator(data_dir=args.data_dir)
    
    # Train specific domains or all
    if len(args.domains) < len(DomainComparator.DOMAINS):
        logger.info(f"Training selected domains: {args.domains}")
        for domain in args.domains:
            comparator.train_domain(domain, epochs=args.epochs)
            comparator.evaluate_domain(domain)
    else:
        logger.info("Training all domains")
        comparator.compare_all_domains(epochs=args.epochs)
    
    # Generate report
    comparator.generate_comparison_report()
    
    # Save results
    comparator.save_results()
    
    # Plot results
    if args.plot:
        comparator.plot_comparison()


if __name__ == '__main__':
    main()
