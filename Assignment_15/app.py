"""
Assignment 15: Train classifier for multiple fruits and vegetables
Extends single-fruit classifier to recognize multiple fruit types
"""

import os
import json
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime

# TensorFlow imports
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

class MultifruitClassifier:
    """
    Multi-fruit image classifier using transfer learning
    Trained to distinguish between multiple fruit types
    """
    
    def __init__(self, model_name='multifruits_model'):
        self.model_name = model_name
        self.model = None
        self.fruit_classes = []
        self.class_indices = {}
        self.history = None
        
    def prepare_data(self, data_dir='fruit_data'):
        """
        Prepare training data from directory structure
        Expected structure:
        fruit_data/
            ├── apple/
            ├── banana/
            ├── orange/
            ├── tomato/
            └── ... (other fruits)
        """
        
        if not os.path.exists(data_dir):
            print(f"❌ Data directory '{data_dir}' not found!")
            print("Please create the following structure:")
            print(f"""
{data_dir}/
    ├── apple/
    │   ├── apple_1.jpg
    │   └── ...
    ├── banana/
    ├── orange/
    ├── tomato/
    └── ... (other fruits)
            """)
            return False
        
        # Get fruit classes from subdirectories
        self.fruit_classes = sorted([d for d in os.listdir(data_dir) 
                                     if os.path.isdir(os.path.join(data_dir, d))])
        self.class_indices = {fruit: idx for idx, fruit in enumerate(self.fruit_classes)}
        
        print(f"\n✅ Found {len(self.fruit_classes)} fruit classes: {self.fruit_classes}")
        
        return True
    
    def build_model(self, input_shape=(224, 224, 3)):
        """
        Build transfer learning model using MobileNetV2
        Advantages:
        - Lightweight (good for IoT devices)
        - Fast training and inference
        - Pre-trained on ImageNet
        """
        
        # Load pre-trained MobileNetV2
        base_model = MobileNetV2(
            input_shape=input_shape,
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model layers (transfer learning)
        base_model.trainable = False
        
        # Build custom head for our fruit classes
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(len(self.fruit_classes), activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=1e-3),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        print(f"\n✅ Model built with {len(self.fruit_classes)} output classes")
        print(f"Model parameters: {model.count_params():,}")
        
        return model
    
    def train(self, data_dir='fruit_data', epochs=20, batch_size=32, test_split=0.2):
        """
        Train the multi-fruit classifier
        """
        
        if not self.prepare_data(data_dir):
            return False
        
        if self.model is None:
            self.build_model()
        
        # Load and preprocess images
        print("\n📸 Loading training data...")
        
        all_images = []
        all_labels = []
        
        for fruit_idx, fruit in enumerate(self.fruit_classes):
            fruit_dir = os.path.join(data_dir, fruit)
            image_files = [f for f in os.listdir(fruit_dir) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            print(f"  Loading {fruit}: {len(image_files)} images")
            
            for img_file in image_files:
                img_path = os.path.join(fruit_dir, img_file)
                try:
                    img = image.load_img(img_path, target_size=(224, 224))
                    img_array = image.img_to_array(img)
                    img_array = preprocess_input(img_array)
                    all_images.append(img_array)
                    all_labels.append(fruit_idx)
                except Exception as e:
                    print(f"    ⚠️ Error loading {img_file}: {e}")
        
        if len(all_images) == 0:
            print("\n❌ No images found! Please add fruit images to the data directory.")
            return False
        
        # Convert to numpy arrays
        X = np.array(all_images)
        y = keras.utils.to_categorical(all_labels, num_classes=len(self.fruit_classes))
        
        # Split data
        split_idx = int(len(X) * (1 - test_split))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        print(f"\n✅ Data loaded successfully!")
        print(f"  Total images: {len(X)}")
        print(f"  Training set: {len(X_train)} images")
        print(f"  Test set: {len(X_test)} images")
        
        # Train model
        print(f"\n🚀 Training model for {epochs} epochs...")
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )
        
        # Evaluate
        test_loss, test_accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"\n✅ Training complete!")
        print(f"  Test Accuracy: {test_accuracy*100:.2f}%")
        print(f"  Test Loss: {test_loss:.4f}")
        
        return True
    
    def predict(self, image_path, confidence_threshold=0.5):
        """
        Predict fruit type from image
        Returns: (fruit_name, confidence, all_predictions)
        """
        
        if self.model is None:
            print("❌ Model not trained yet!")
            return None
        
        # Load and preprocess image
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = preprocess_input(img_array)
        img_batch = np.expand_dims(img_array, axis=0)
        
        # Predict
        predictions = self.model.predict(img_batch, verbose=0)[0]
        
        # Get results
        predicted_idx = np.argmax(predictions)
        predicted_fruit = self.fruit_classes[predicted_idx]
        confidence = predictions[predicted_idx]
        
        # All predictions with confidence
        all_predictions = {
            self.fruit_classes[i]: float(predictions[i]) 
            for i in range(len(self.fruit_classes))
        }
        
        # Sort by confidence
        sorted_predictions = dict(sorted(all_predictions.items(), 
                                         key=lambda x: x[1], reverse=True))
        
        return {
            'prediction': predicted_fruit,
            'confidence': float(confidence),
            'all_predictions': sorted_predictions,
            'high_confidence': confidence >= confidence_threshold
        }
    
    def test_similar_fruits(self, test_images_dir='test_images'):
        """
        Test with similar fruits to see how well classifier distinguishes them
        Example: apples vs tomatoes (both can be red, round)
        """
        
        if self.model is None:
            print("❌ Model not trained yet!")
            return
        
        if not os.path.exists(test_images_dir):
            print(f"⚠️ Test directory '{test_images_dir}' not found")
            return
        
        print(f"\n🧪 Testing classifier with similar fruits...")
        print("=" * 60)
        
        test_files = [f for f in os.listdir(test_images_dir) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        correct = 0
        total = 0
        
        for test_file in test_files:
            test_path = os.path.join(test_images_dir, test_file)
            result = self.predict(test_path)
            
            # Try to extract true label from filename (e.g., "apple_1.jpg" -> "apple")
            true_label = test_file.split('_')[0].lower()
            predicted_label = result['prediction'].lower()
            is_correct = true_label == predicted_label
            
            total += 1
            if is_correct:
                correct += 1
            
            status = "✅" if is_correct else "❌"
            print(f"{status} {test_file}")
            print(f"   Expected: {true_label}")
            print(f"   Predicted: {predicted_label} ({result['confidence']*100:.1f}%)")
            print(f"   All predictions: {result['all_predictions']}")
            print()
        
        if total > 0:
            accuracy = correct / total * 100
            print("=" * 60)
            print(f"Test Accuracy: {accuracy:.1f}% ({correct}/{total})")
    
    def save_model(self):
        """Save trained model"""
        if self.model is None:
            print("❌ No model to save!")
            return
        
        model_path = f'{self.model_name}.h5'
        self.model.save(model_path)
        print(f"✅ Model saved to {model_path}")
        
        # Save class information
        info = {
            'fruit_classes': self.fruit_classes,
            'class_indices': self.class_indices,
            'timestamp': datetime.now().isoformat()
        }
        
        info_path = f'{self.model_name}_info.json'
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        print(f"✅ Class info saved to {info_path}")
    
    def plot_training_history(self):
        """Plot training history"""
        if self.history is None:
            print("❌ No training history available!")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        
        # Accuracy
        axes[0].plot(self.history.history['accuracy'], label='Training')
        axes[0].plot(self.history.history['val_accuracy'], label='Validation')
        axes[0].set_title('Model Accuracy')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Accuracy')
        axes[0].legend()
        axes[0].grid(True)
        
        # Loss
        axes[1].plot(self.history.history['loss'], label='Training')
        axes[1].plot(self.history.history['val_loss'], label='Validation')
        axes[1].set_title('Model Loss')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Loss')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.savefig(f'{self.model_name}_training.png')
        print(f"✅ Training history plot saved to {self.model_name}_training.png")
        plt.show()


def main():
    """Main function to demonstrate multi-fruit classifier"""
    
    print("🍎 Multi-Fruit Image Classifier Training")
    print("=" * 60)
    
    # Initialize classifier
    classifier = MultifruitClassifier('multifruits_model')
    
    # Train model
    print("\n1️⃣ TRAINING PHASE")
    print("-" * 60)
    success = classifier.train(
        data_dir='fruit_data',
        epochs=20,
        batch_size=32
    )
    
    if not success:
        print("\n⚠️ Training failed. Please check your data directory.")
        return
    
    # Plot training results
    print("\n2️⃣ ANALYZING TRAINING RESULTS")
    print("-" * 60)
    classifier.plot_training_history()
    
    # Test on similar fruits
    print("\n3️⃣ TESTING WITH SIMILAR FRUITS")
    print("-" * 60)
    classifier.test_similar_fruits('test_images')
    
    # Save model
    print("\n4️⃣ SAVING MODEL")
    print("-" * 60)
    classifier.save_model()
    
    # Example single prediction
    print("\n5️⃣ EXAMPLE PREDICTIONS")
    print("-" * 60)
    test_image = 'test_images/apple_sample.jpg'
    if os.path.exists(test_image):
        result = classifier.predict(test_image)
        print(f"Image: {test_image}")
        print(f"Prediction: {result['prediction']}")
        print(f"Confidence: {result['confidence']*100:.1f}%")


if __name__ == '__main__':
    main()
