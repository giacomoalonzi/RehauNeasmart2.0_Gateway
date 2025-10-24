#!/usr/bin/env python3

"""
Main entry point for the Rehau Neasmart Gateway application.

This module initializes and starts both the Flask REST API server
and the Modbus server (TCP or Serial).
"""

import asyncio
import logging
import sys

from app_factory import create_app, start_flask_server
from config import config_manager
from modbus_server import run_modbus_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./data/gateway.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

_logger = logging.getLogger(__name__)


def main():
    """
    Main function to initialize and start the gateway application.
    
    This function:
    1. Loads configuration from options.json
    2. Creates and configures the Flask application
    3. Starts the Flask REST API server in a separate thread
    4. Starts the Modbus server (TCP or Serial) in the main event loop
    """
    try:
        # Load configuration
        _logger.info("Loading configuration...")
        config = config_manager.get_config()
        _logger.info(f"Configuration loaded: {config}")
        
        # Create Flask application
        _logger.info("Creating Flask application...")
        app = create_app(config)
        
        # Start Flask server in separate thread
        _logger.info(f"Starting Flask server on 0.0.0.0:{config.server_port}...")
        start_flask_server(app, host='0.0.0.0', port=config.server_port)
        
        # Prepare Modbus server address based on connection type
        if config.server_type == "tcp":
            modbus_addr = (config.listen_address, config.listen_port)
            _logger.info(f"Preparing Modbus TCP server on {config.listen_address}:{config.listen_port}")
        elif config.server_type == "serial":
            modbus_addr = config.listen_address
            _logger.info(f"Preparing Modbus Serial server on {config.listen_address}")
        else:
            _logger.critical(f"Unsupported server type: {config.server_type}")
            sys.exit(1)
        
        # Get Modbus context from Flask app
        context = app.config['MODBUS_CONTEXT']
        
        # Start Modbus server
        _logger.info("Starting Modbus server...")
        asyncio.run(run_modbus_server(context, modbus_addr, config.server_type))
        
    except KeyboardInterrupt:
        _logger.info("Application stopped by user")
        sys.exit(0)
    except Exception as e:
        _logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()