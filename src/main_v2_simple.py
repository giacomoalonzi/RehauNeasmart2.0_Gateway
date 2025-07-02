#!/usr/bin/env python3
"""
Rehau Neasmart 2.0 Gateway - Simplified Test Version
Basic version to demonstrate the new architecture without complex dependencies.
"""

import json
import logging
import sys
import threading
import time
from flask import Flask, request, jsonify

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Basic configuration from file
def load_config():
    """Load configuration from file with fallbacks"""
    try:
        with open('../data/config.json', 'r') as f:
            config = json.load(f)
        logger.info("Configuration loaded successfully")
        return config
    except Exception as e:
        logger.warning(f"Failed to load config: {e}, using defaults")
        return {
            "api": {"host": "0.0.0.0", "port": 5001},
            "debug_mode": True
        }

# Create Flask app
def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    
    @app.before_request
    def before_request():
        start_time = time.time()
        app.start_time = start_time
    
    @app.after_request
    def after_request(response):
        if hasattr(app, 'start_time'):
            duration = (time.time() - app.start_time) * 1000
            logger.info(f"{request.method} {request.path} - {response.status_code} - {duration:.2f}ms")
        return response
    
    @app.errorhandler(500)
    def handle_error(error):
        logger.exception("Internal server error")
        return jsonify({
            'error': 'Internal server error',
            'status': 500
        }), 500
    
    # Basic health endpoint
    @app.route("/health")
    def health():
        """Enhanced health check"""
        return jsonify({
            "status": "healthy",
            "version": "2.0.0-simplified",
            "timestamp": time.time(),
            "components": {
                "api": "running",
                "database": "simulated",
                "modbus": "simulated"
            }
        }), 200
    
    # Simulate the legacy API endpoints
    @app.route("/outsidetemperature", methods=['GET'])
    def get_outside_temp():
        """Simulated outside temperature"""
        return jsonify({
            "outside_temperature": 18.5,
            "filtered_outside_temperature": 18.2,
            "source": "simulated"
        }), 200
    
    @app.route("/notifications", methods=['GET'])
    def get_notifications():
        """Simulated notifications"""
        return jsonify({
            "hints_present": False,
            "warnings_present": False,
            "error_present": False,
            "source": "simulated"
        }), 200
    
    @app.route("/mode", methods=['GET', 'POST'])
    def mode():
        """Simulated mode operations"""
        if request.method == 'GET':
            return jsonify({"mode": 1, "source": "simulated"}), 200
        elif request.method == 'POST':
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            payload = request.get_json()
            mode = payload.get("mode")
            
            if mode is None:
                return jsonify({'error': 'Missing mode key'}), 400
            
            if not isinstance(mode, int) or mode <= 0 or mode > 5:
                return jsonify({'error': 'Invalid mode (1-5)'}), 400
            
            logger.info(f"Mode change simulated: {mode}")
            return jsonify({'mode': mode, 'status': 'accepted'}), 202
    
    @app.route("/zones/<int:base_id>/<int:zone_id>", methods=['GET', 'POST'])
    def zone(base_id, zone_id):
        """Simulated zone operations"""
        if base_id < 1 or base_id > 4 or zone_id < 1 or zone_id > 16:
            return jsonify({'error': 'Invalid base_id (1-4) or zone_id (1-16)'}), 400
        
        if request.method == 'GET':
            return jsonify({
                "base_id": base_id,
                "zone_id": zone_id,
                "temperature": 21.5,
                "humidity": 45,
                "setpoint": 22.0,
                "mode": 1,
                "source": "simulated"
            }), 200
        
        elif request.method == 'POST':
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            payload = request.get_json()
            logger.info(f"Zone {base_id}/{zone_id} update simulated: {payload}")
            
            return jsonify({
                'base_id': base_id,
                'zone_id': zone_id,
                'status': 'accepted',
                'payload': payload
            }), 202
    
    @app.route("/api/v1/zones", methods=['GET'])
    def api_zones():
        """New API endpoint for zones"""
        return jsonify({
            "zones": [
                {"base_id": 1, "zone_id": i, "temperature": 20 + i, "status": "active"}
                for i in range(1, 5)
            ],
            "total": 4,
            "api_version": "v1"
        }), 200
    
    logger.info("Flask app created with simulated endpoints")
    return app

def main():
    """Main entry point"""
    try:
        logger.info("Starting Rehau Neasmart 2.0 Gateway - Simplified Version")
        
        # Load configuration
        config = load_config()
        
        # Create app
        app = create_app()
        
        # Log startup info
        api_config = config.get('api', {})
        host = api_config.get('host', '0.0.0.0')
        port = api_config.get('port', 5001)
        debug = config.get('debug_mode', True)
        
        logger.info(f"Starting API server on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        logger.info("Available endpoints:")
        logger.info("  GET  /health")
        logger.info("  GET  /outsidetemperature")
        logger.info("  GET  /notifications")
        logger.info("  GET/POST /mode")
        logger.info("  GET/POST /zones/<base_id>/<zone_id>")
        logger.info("  GET  /api/v1/zones")
        
        # Run the app
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.exception(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 