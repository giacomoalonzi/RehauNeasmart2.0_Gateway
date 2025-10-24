#!/usr/bin/env python3

import asyncio
import logging
import threading
from app_factory import create_app, start_flask_server
from modbus_server import start_modbus_server
from config import config_manager

# Setup logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


def main():
    """Main application entry point."""
    try:
        # Load configuration
        config = config_manager.get_config()
        _logger.info(f"Starting Rehau Neasmart Gateway with config: {config}")
        
        # Create Flask application
        app = create_app(config)
        
        # Start Flask server in separate thread
        flask_thread = start_flask_server(app, host='0.0.0.0', port=config.server_port)
        _logger.info(f"Flask server started on port {config.server_port}")
        
        # Start Modbus server (blocking)
        _logger.info(f"Starting Modbus server: {config.server_type} on {config.listen_address}:{config.listen_port}")
        start_modbus_server(config)
        
    except KeyboardInterrupt:
        _logger.info("Shutting down gracefully...")
    except Exception as e:
        _logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
