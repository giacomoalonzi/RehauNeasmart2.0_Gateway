#!/usr/bin/env python3

import logging
import threading
from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from config import config_manager
from modbus_server import setup_server_context
from openapi_generator import generate_openapi_yaml, get_openapi_dict
import const

_logger = logging.getLogger(__name__)


def create_app(config=None):
    """
    Create and configure Flask application.
    
    Args:
        config: Optional configuration object
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        config = config_manager.get_config()
    
    # Store configuration in app context
    app.config['SERVER_CONFIG'] = config
    
    # Initialize Modbus context
    context = setup_server_context(const.DATASTORE_PATH, config.slave_id)
    app.config['MODBUS_CONTEXT'] = context
    app.config['SLAVE_ID'] = config.slave_id
    
    # Register blueprints
    from api import register_blueprints
    register_blueprints(app)
    
    # Register Swagger UI
    swaggerui_blueprint = get_swaggerui_blueprint(
        '/api/docs',
        '/api/openapi.yaml',
        config={
            'app_name': "Rehau Neasmart 2.0 Gateway API",
            'supportedSubmitMethods': ['get', 'post', 'put', 'delete'],
            'validatorUrl': None
        }
    )
    app.register_blueprint(swaggerui_blueprint)
    
    # Add OpenAPI YAML endpoint
    @app.route('/api/openapi.yaml')
    def openapi_yaml():
        """Serve OpenAPI specification in YAML format."""
        try:
            yaml_content = generate_openapi_yaml(app)
            return yaml_content, 200, {'Content-Type': 'application/x-yaml'}
        except Exception as e:
            _logger.error(f"Error generating OpenAPI YAML: {e}")
            return jsonify({'error': 'Failed to generate OpenAPI specification'}), 500
    
    # Add OpenAPI JSON endpoint
    @app.route('/api/openapi.json')
    def openapi_json():
        """Serve OpenAPI specification in JSON format."""
        try:
            spec_dict = get_openapi_dict(app)
            return jsonify(spec_dict)
        except Exception as e:
            _logger.error(f"Error generating OpenAPI JSON: {e}")
            return jsonify({'error': 'Failed to generate OpenAPI specification'}), 500
    
    _logger.info("Flask application created and configured")
    return app


def start_flask_server(app, host='0.0.0.0', port=5001):
    """
    Start Flask server in a separate thread.
    
    Args:
        app (Flask): Flask application instance
        host (str): Host address
        port (int): Port number
    """
    def run_server():
        app.run(host=host, port=port, debug=False, use_reloader=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    _logger.info(f"Flask server started on {host}:{port}")
    return server_thread
