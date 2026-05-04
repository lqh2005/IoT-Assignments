"""
Azure Function for IoT Edge
Runs containerized on edge device - processes IoT Hub data locally
No cloud latency, works offline
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from datetime import datetime
import threading

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import route handlers
from route_handler import FruitClassificationHandler, IoTHubEventHandler

# Initialize handlers
classification_handler = FruitClassificationHandler()
iot_handler = IoTHubEventHandler()

# Statistics
stats = {
    'total_requests': 0,
    'successful_processing': 0,
    'errors': 0,
    'start_time': datetime.now().isoformat(),
    'messages_processed': 0
}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for container orchestration"""
    
    return jsonify({
        'status': 'healthy',
        'uptime': str(datetime.now() - datetime.fromisoformat(stats['start_time'])),
        'messages_processed': stats['messages_processed']
    }), 200


@app.route('/classify', methods=['POST'])
def classify_fruit():
    """
    HTTP trigger for fruit classification
    Processes base64 encoded image and returns ripeness classification
    
    Request body:
    {
        "image_data": "base64_encoded_image",
        "fruit_type": "apple",
        "device_id": "camera-01"
    }
    """
    
    stats['total_requests'] += 1
    
    try:
        data = request.get_json()
        
        if not data:
            logger.error("Empty request body")
            stats['errors'] += 1
            return jsonify({'error': 'Empty request body'}), 400
        
        # Process classification request
        result = classification_handler.process_image(data)
        
        if result['success']:
            stats['successful_processing'] += 1
            logger.info(f"Classification successful: {result['prediction']}")
            return jsonify(result), 200
        else:
            stats['errors'] += 1
            logger.error(f"Classification failed: {result['error']}")
            return jsonify(result), 400
            
    except Exception as e:
        stats['errors'] += 1
        logger.exception(f"Error in /classify: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/process-iot-event', methods=['POST'])
def process_iot_event():
    """
    HTTP trigger for processing IoT Hub events
    Simulates IoT Hub trigger on edge device
    
    Request body:
    {
        "device_id": "device-01",
        "sensor_data": {...},
        "timestamp": "2026-05-04T..."
    }
    """
    
    stats['total_requests'] += 1
    
    try:
        data = request.get_json()
        
        if not data:
            logger.error("Empty event body")
            stats['errors'] += 1
            return jsonify({'error': 'Empty event body'}), 400
        
        # Process IoT event
        result = iot_handler.process_event(data)
        stats['messages_processed'] += 1
        
        logger.info(f"IoT event processed: {result['message']}")
        return jsonify(result), 200
        
    except Exception as e:
        stats['errors'] += 1
        logger.exception(f"Error in /process-iot-event: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/store-blob', methods=['POST'])
def store_blob():
    """
    HTTP trigger for storing data to local blob storage (edge)
    Simulates Azure Blob Storage on edge device
    
    Request body:
    {
        "filename": "sensor_data_2026-05-04.json",
        "data": {...}
    }
    """
    
    stats['total_requests'] += 1
    
    try:
        data = request.get_json()
        
        filename = data.get('filename', f'data_{datetime.now().timestamp()}.json')
        content = data.get('data', {})
        
        # Store to local directory (simulating blob storage)
        os.makedirs('edge_storage', exist_ok=True)
        
        filepath = os.path.join('edge_storage', filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'data': content
            }, f, indent=2)
        
        stats['successful_processing'] += 1
        
        logger.info(f"Data stored: {filepath}")
        return jsonify({
            'success': True,
            'message': f'Data stored to {filepath}',
            'filepath': filepath
        }), 200
        
    except Exception as e:
        stats['errors'] += 1
        logger.exception(f"Error in /store-blob: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get function statistics"""
    
    return jsonify({
        'statistics': stats,
        'current_time': datetime.now().isoformat()
    }), 200


@app.route('/logs', methods=['GET'])
def get_logs():
    """Get recent logs"""
    
    try:
        with open('edge_storage/function.log', 'r') as f:
            logs = f.readlines()[-100:]  # Last 100 lines
        
        return jsonify({
            'logs': logs,
            'count': len(logs)
        }), 200
    except:
        return jsonify({
            'message': 'No logs available',
            'logs': []
        }), 200


@app.route('/shutdown', methods=['POST'])
def shutdown_function():
    """Graceful shutdown endpoint"""
    
    logger.info("Shutdown requested")
    
    # In real scenario, this would trigger proper cleanup
    return jsonify({
        'message': 'Shutdown initiated',
        'final_stats': stats
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    stats['errors'] += 1
    return jsonify({'error': 'Internal server error'}), 500


def run_edge_function():
    """Run the edge function with proper configuration"""
    
    logger.info("=" * 70)
    logger.info("🚀 Azure Function on IoT Edge starting...")
    logger.info("=" * 70)
    
    logger.info(f"📍 Environment: IoT Edge Container")
    logger.info(f"🔌 Listening on 0.0.0.0:8000")
    logger.info(f"⏱️ Started: {datetime.now().isoformat()}")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False,
        threaded=True,
        use_reloader=False
    )


if __name__ == '__main__':
    run_edge_function()
