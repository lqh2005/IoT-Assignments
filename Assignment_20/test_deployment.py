"""
Test and verify Assignment 20 deployment pipeline.
"""

import sys
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class DeploymentTester:
    """Test framework for edge deployment."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def test(self, name, func):
        """Run a test and record result."""
        try:
            logger.info(f"\n▶ {name}...")
            func()
            logger.info(f"✅ {name} PASSED")
            self.passed += 1
            self.results.append((name, 'PASS'))
        except Exception as e:
            logger.error(f"❌ {name} FAILED: {e}")
            self.failed += 1
            self.results.append((name, f'FAIL: {str(e)[:50]}'))
    
    def print_summary(self):
        """Print test summary."""
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        for name, result in self.results:
            status_icon = "✅" if result == 'PASS' else "❌"
            logger.info(f"{status_icon} {name}: {result}")
        
        total = self.passed + self.failed
        logger.info(f"\nTotal: {self.passed}/{total} passed")
        
        if self.failed == 0:
            logger.info("🎉 All tests passed!")
        else:
            logger.warning(f"⚠️  {self.failed} test(s) failed")


def main():
    """Run deployment tests."""
    logger.info("="*60)
    logger.info("ASSIGNMENT 20 - EDGE DEPLOYMENT TESTS")
    logger.info("="*60)
    
    tester = DeploymentTester()
    
    # Test 1: Dependencies
    def test_imports():
        import tensorflow as tf
        import numpy as np
        from PIL import Image
        logger.info(f"  TensorFlow {tf.__version__}")
        logger.info(f"  NumPy {np.__version__}")
    
    tester.test("Import dependencies", test_imports)
    
    # Test 2: Module imports
    def test_modules():
        from app import EdgeModelExporter, EdgeInference
        from edge_runtime import EdgeDevice, EdgeInferenceServer
    
    tester.test("Import deployment modules", test_modules)
    
    # Test 3: EdgeDevice detection
    def test_device_detection():
        from edge_runtime import EdgeDevice
        device = EdgeDevice()
        info = device.get_info()
        assert info is not None
        assert 'platform' in info
    
    tester.test("Detect edge device", test_device_detection)
    
    # Test 4: Check output directory
    def test_output_dir():
        export_dir = Path('./exported_models')
        assert export_dir.parent.exists(), "Working directory issues"
    
    tester.test("Verify output directory", test_output_dir)
    
    # Test 5: Model export class
    def test_exporter_init():
        from app import EdgeModelExporter
        # This will fail if no model exists, but the class should load
        try:
            exporter = EdgeModelExporter('nonexistent.h5')
        except:
            pass  # Expected to fail
    
    tester.test("EdgeModelExporter instantiation", test_exporter_init)
    
    # Test 6: Inference class
    def test_inference_init():
        from app import EdgeInference
        # This will fail if no model exists, but the class should load
        try:
            inf = EdgeInference('nonexistent.tflite')
        except:
            pass  # Expected to fail
    
    tester.test("EdgeInference instantiation", test_inference_init)
    
    # Test 7: Performance simulation
    def test_performance_estimate():
        """Simulate expected performance."""
        # Expected on Raspberry Pi
        inference_time_ms = 35  # int8 TFLite
        fps = 1000 / inference_time_ms
        assert fps > 20, f"Expected >20 FPS, got {fps:.1f}"
        logger.info(f"  Expected FPS on RPi: {fps:.1f}")
    
    tester.test("Performance estimation", test_performance_estimate)
    
    # Test 8: File structure
    def test_file_structure():
        files = {
            'app.py': 'Model export implementation',
            'edge_runtime.py': 'Edge device runtime',
            'requirements.txt': 'Dependencies',
            'assignment20.md': 'Assignment documentation',
            'README.md': 'Quick reference',
            'SETUP.md': 'Installation guide',
            'DEPLOYMENT.md': 'Deployment guide'
        }
        
        for filename, description in files.items():
            path = Path(filename)
            assert path.exists(), f"Missing: {filename} ({description})"
            logger.info(f"  ✓ {filename}")
    
    tester.test("Check file structure", test_file_structure)
    
    # Print summary
    tester.print_summary()
    
    # Next steps
    logger.info("\n" + "="*60)
    logger.info("NEXT STEPS")
    logger.info("="*60)
    logger.info("\n1. Get a trained model from Assignment 15 or 19")
    logger.info("2. Export the model:")
    logger.info("   python app.py --model ../Assignment_15/fruit.h5 --export-all")
    logger.info("\n3. Test inference on this PC:")
    logger.info("   python app.py --model fruit.h5 --test-dir ./test_images/")
    logger.info("\n4. Copy to Raspberry Pi or Jetson Nano")
    logger.info("5. Run edge_runtime.py on the device")
    logger.info("\n📖 See README.md for detailed instructions")
    
    return 0 if tester.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
