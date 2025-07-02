#!/usr/bin/env python3
"""
Rehau Neasmart 2.0 Gateway - Refactored Version
Production-ready application with robust error handling and fallbacks.
"""

import asyncio
import signal
import sys
import threading
import time
import json
import logging
from typing import Dict, Any
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Import our robust components
from config import get_config, ConfigError
from logger_setup import setup_logging, get_logger, log_api_request
from database import get_database_manager, close_database_manager
from modbus_manager import get_modbus_manager, close_modbus_manager, ModbusException
from api.zones import zones_bp
import const
import dpt_9001

# Import original Modbus server components
from pymodbus.framer import ModbusRtuFramer, ModbusSocketFramer
from pymodbus.server import StartAsyncSerialServer, StartAsyncTcpServer
from pymodbus import __version__ as pymodbus_version

# Initialize logger
logger = get_logger(__name__)

# Global variables for graceful shutdown
shutdown_event = threading.Event()
modbus_server_task = None


def create_app(config=None):
    """Create Flask application with configuration"""
    
    # Load configuration
    if config is None:
        try:
            config = get_config()
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
    
    # Setup logging
    setup_logging(config.logging, "neasmart-gateway")
    logger.info("Starting Rehau Neasmart 2.0 Gateway v2.0")
    
    # Initialize Flask app
    app = Flask(__name__)
    app.config['CONFIG'] = config
    
    # Initialize CORS
    if config.api.enable_cors:
        CORS(app, origins=config.api.cors_origins)
        logger.info(f"CORS enabled for origins: {config.api.cors_origins}")
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[f"{config.api.rate_limit_per_minute} per minute"]
    )
    logger.info(f"Rate limiting: {config.api.rate_limit_per_minute} requests per minute")
    
    # Request logging middleware
    @app.before_request
    def before_request():
        g.start_time = time.time()
        
        # API key authentication (if enabled)
        if config.api.enable_auth and request.endpoint != 'health':
            api_key = request.headers.get('X-API-Key')
            if not api_key or api_key != config.api.api_key:
                logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
                return jsonify({
                    'error': 'Invalid or missing API key',
                    'status': 401
                }), 401
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration_ms = (time.time() - g.start_time) * 1000
            user = 'authenticated' if config.api.enable_auth else 'anonymous'
            log_api_request(
                logger,
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                user
            )
        return response
    
    # Error handlers
    @app.errorhandler(ModbusException)
    def handle_modbus_error(error):
        logger.error(f"Modbus error: {error}")
        return jsonify({
            'error': 'Communication error with Modbus device',
            'details': str(error),
            'status': 503
        }), 503
    
    @app.errorhandler(429)
    def handle_rate_limit(error):
        logger.warning(f"Rate limit exceeded: {request.remote_addr}")
        return jsonify({
            'error': 'Rate limit exceeded',
            'status': 429
        }), 429
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.exception("Internal server error")
        return jsonify({
            'error': 'Internal server error',
            'status': 500
        }), 500
    
    # Register blueprints
    app.register_blueprint(zones_bp)
    logger.info("API blueprints registered")
    
    # Legacy endpoints for backward compatibility
    register_legacy_endpoints(app, config)
    
    return app


def register_legacy_endpoints(app, config):
    """Register legacy endpoints for backward compatibility"""
    
    @app.route("/outsidetemperature", methods=['GET'])
    def get_outside_temp():
        """Get outside temperature readings"""
        try:
            modbus = get_modbus_manager()
            
            outside_temp_raw = modbus.read_register(const.OUTSIDE_TEMP_REG)
            filtered_temp_raw = modbus.read_register(const.FILTERED_OUTSIDE_TEMP_REG)
            
            data = {
                "outside_temperature": dpt_9001.unpack_dpt9001(outside_temp_raw),
                "filtered_outside_temperature": dpt_9001.unpack_dpt9001(filtered_temp_raw)
            }
            
            return jsonify(data), 200
            
        except Exception as e:
            logger.error(f"Failed to read outside temperature: {e}")
            return jsonify({
                'error': 'Failed to read outside temperature',
                'details': str(e),
                'status': 503
            }), 503
    
    @app.route("/notifications", methods=['GET'])
    def get_notifications():
        """Get system notifications"""
        try:
            modbus = get_modbus_manager()
            
            data = {
                "hints_present": modbus.read_register(const.HINTS_PRESENT_ADDR) == 1,
                "warnings_present": modbus.read_register(const.WARNINGS_PRESENT_ADDR) == 1,
                "error_present": modbus.read_register(const.ERRORS_PRESENT_ADDR) == 1
            }
            
            return jsonify(data), 200
            
        except Exception as e:
            logger.error(f"Failed to read notifications: {e}")
            return jsonify({
                'error': 'Failed to read notifications',
                'details': str(e),
                'status': 503
            }), 503
    
    @app.route("/mode", methods=['POST', 'GET'])
    def mode():
        """Get/Set global operation mode"""
        try:
            modbus = get_modbus_manager()
            
            if request.method == 'GET':
                mode_value = modbus.read_register(const.GLOBAL_OP_MODE_ADDR)
                return jsonify({"mode": mode_value}), 200
                
            elif request.method == 'POST':
                if not request.is_json:
                    return jsonify({'error': 'Request must be JSON'}), 400
                
                payload = request.get_json()
                op_mode = payload.get("mode")
                
                if op_mode is None:
                    return jsonify({'error': 'Missing mode key in payload'}), 400
                
                if not isinstance(op_mode, int) or op_mode <= 0 or op_mode > 5:
                    return jsonify({'error': 'Invalid mode. Must be integer between 1 and 5'}), 400
                
                modbus.write_register(const.GLOBAL_OP_MODE_ADDR, op_mode)
                return jsonify({'mode': op_mode}), 202
                
        except Exception as e:
            logger.error(f"Failed to handle mode operation: {e}")
            return jsonify({
                'error': 'Failed to handle mode operation',
                'details': str(e),
                'status': 503
            }), 503
    
    @app.route("/state", methods=['POST', 'GET'])
    def state():
        """Get/Set global operation state"""
        try:
            modbus = get_modbus_manager()
            
            if request.method == 'GET':
                state_value = modbus.read_register(const.GLOBAL_OP_STATE_ADDR)
                return jsonify({"state": state_value}), 200
                
            elif request.method == 'POST':
                if not request.is_json:
                    return jsonify({'error': 'Request must be JSON'}), 400
                
                payload = request.get_json()
                op_state = payload.get("state")
                
                if op_state is None:
                    return jsonify({'error': 'Missing state key in payload'}), 400
                
                if not isinstance(op_state, int) or op_state <= 0 or op_state > 6:
                    return jsonify({'error': 'Invalid state. Must be integer between 1 and 6'}), 400
                
                modbus.write_register(const.GLOBAL_OP_STATE_ADDR, op_state)
                return jsonify({'state': op_state}), 202
                
        except Exception as e:
            logger.error(f"Failed to handle state operation: {e}")
            return jsonify({
                'error': 'Failed to handle state operation',
                'details': str(e),
                'status': 503
            }), 503
    
    @app.route("/mixedgroups/<int:group_id>", methods=['GET'])
    def get_mixed_circuit(group_id):
        """Get mixed circuit information"""
        try:
            if group_id <= 0 or group_id > 3:
                return jsonify({'error': 'Invalid mixed group ID. Must be between 1 and 3'}), 400
            
            modbus = get_modbus_manager()
            base_reg = const.MIXEDGROUP_BASE_REG[group_id]
            
            pump_state = modbus.read_register(base_reg + const.MIXEDGROUP_PUMP_STATE_OFFSET)
            valve_opening = modbus.read_register(base_reg + const.MIXEDGROUP_VALVE_OPENING_OFFSET)
            flow_temp_raw = modbus.read_register(base_reg + const.MIXEDGROUP_FLOW_TEMP_OFFSET)
            return_temp_raw = modbus.read_register(base_reg + const.MIXEDGROUP_RETURN_TEMP_OFFSET)
            
            data = {
                "group_id": group_id,
                "pump_state": pump_state,
                "mixing_valve_opening_percentage": valve_opening,
                "flow_temperature": dpt_9001.unpack_dpt9001(flow_temp_raw),
                "return_temperature": dpt_9001.unpack_dpt9001(return_temp_raw)
            }
            
            return jsonify(data), 200
            
        except Exception as e:
            logger.error(f"Failed to read mixed group {group_id}: {e}")
            return jsonify({
                'error': f'Failed to read mixed group {group_id}',
                'details': str(e),
                'status': 503
            }), 503
    
    @app.route("/dehumidifiers/<int:dehumidifier_id>", methods=['GET'])
    def get_dehumidifier(dehumidifier_id):
        """Get dehumidifier status"""
        try:
            if dehumidifier_id <= 0 or dehumidifier_id > 9:
                return jsonify({'error': 'Invalid dehumidifier ID. Must be between 1 and 9'}), 400
            
            modbus = get_modbus_manager()
            dehumidifier_state = modbus.read_register(
                dehumidifier_id + const.DEHUMIDIFIERS_ADDR_OFFSET
            )
            
            data = {
                "dehumidifier_id": dehumidifier_id,
                "dehumidifier_state": dehumidifier_state
            }
            
            return jsonify(data), 200
            
        except Exception as e:
            logger.error(f"Failed to read dehumidifier {dehumidifier_id}: {e}")
            return jsonify({
                'error': f'Failed to read dehumidifier {dehumidifier_id}',
                'details': str(e),
                'status': 503
            }), 503
    
    @app.route("/pumps/<int:pump_id>", methods=['GET'])
    def get_extra_pumps(pump_id):
        """Get extra pump status"""
        try:
            if pump_id <= 0 or pump_id > 5:
                return jsonify({'error': 'Invalid pump ID. Must be between 1 and 5'}), 400
            
            modbus = get_modbus_manager()
            pump_state = modbus.read_register(pump_id + const.EXTRA_PUMPS_ADDR_OFFSET)
            
            data = {
                "pump_id": pump_id,
                "pump_state": pump_state
            }
            
            return jsonify(data), 200
            
        except Exception as e:
            logger.error(f"Failed to read pump {pump_id}: {e}")
            return jsonify({
                'error': f'Failed to read pump {pump_id}',
                'details': str(e),
                'status': 503
            }), 503
    
    @app.route("/health")
    def get_health():
        """Enhanced health check endpoint"""
        try:
            modbus = get_modbus_manager()
            db_manager = get_database_manager()
            
            # Get detailed status
            health_data = {
                "status": "healthy",
                "version": "2.0.0",
                "database": db_manager.get_status(),
                "modbus": modbus.get_status(),
                "configuration": {
                    "server_type": config.server.type.value,
                    "api_auth_enabled": config.api.enable_auth,
                    "fallback_enabled": config.database.enable_fallback
                }
            }
            
            # Determine overall health
            if not health_data["database"]["healthy"] and not config.database.enable_fallback:
                health_data["status"] = "unhealthy"
                return jsonify(health_data), 503
            
            if health_data["modbus"]["circuit_breaker"]["state"] == "open":
                health_data["status"] = "degraded"
                return jsonify(health_data), 200
            
            return jsonify(health_data), 200
            
        except Exception as e:
            logger.exception("Health check failed")
            return jsonify({
                "status": "unhealthy",
                "error": str(e)
            }), 503


async def run_modbus_server(config):
    """Run Modbus server with robust error handling"""
    global modbus_server_task
    
    try:
        # Get modbus manager (this initializes the context)
        modbus = get_modbus_manager()
        context = modbus.get_context()
        identity = modbus.get_identity()
        
        # Configure server address
        if config.server.type.value == "tcp":
            server_addr = (config.server.address, config.server.port)
            logger.info(f"Starting Modbus TCP server on {server_addr}")
            
            # Schedule Modbus TCP server as background task
            server_task = asyncio.create_task(
                StartAsyncTcpServer(
                    context=context,
            identity=identity,
            address=server_addr,
            framer=ModbusSocketFramer,
            allow_reuse_address=True,
            ignore_missing_slaves=True,
            broadcast_enable=True,
        )
            )
            
        elif config.server.type.value == "serial":
            server_addr = config.server.serial_port
            logger.info(f"Starting Modbus Serial server on {server_addr}")
            
            # Schedule Modbus Serial server as background task
            server_task = asyncio.create_task(
                StartAsyncSerialServer(
                    context=context,
            identity=identity,
            port=server_addr,
            framer=ModbusRtuFramer,
                    stopbits=config.server.serial_stopbits,
                    bytesize=config.server.serial_bytesize,
                    parity=config.server.serial_parity,
                    baudrate=config.server.serial_baudrate,
            ignore_missing_slaves=True,
            broadcast_enable=True,
        )
            )
        else:
            raise ValueError(f"Unsupported server type: {config.server.type}")
        
        logger.info("Modbus server started successfully (running asynchronously)")
        
        # Wait for shutdown signal
        while not shutdown_event.is_set():
            await asyncio.sleep(1)
        
        logger.info("Shutting down Modbus server...")
        # Cancel the Modbus server task on shutdown
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
        
    except Exception as e:
        logger.exception(f"Modbus server error: {e}")
        shutdown_event.set()


def signal_handler(sig, frame):
    """Immediate exit on shutdown signal"""
    logger.info(f"Received signal {sig}, exiting immediately...")
    shutdown_event.set()
    sys.exit(0)


def initialize_managers(config):
    """Initialize all managers with proper error handling"""
    try:
        # Initialize database manager
        logger.info("Initializing database manager...")
        db_manager = get_database_manager(
            config.database.path,
            table_name=config.database.table_name,
            enable_fallback=config.database.enable_fallback
        )
        logger.info(f"Database manager initialized: {db_manager.get_status()}")
        
        # Initialize modbus manager
        logger.info("Initializing Modbus manager...")
        modbus_manager = get_modbus_manager(
            config.modbus.slave_id,
            database_manager=db_manager
        )
        logger.info(f"Modbus manager initialized: {modbus_manager.get_status()}")
        
        # Sync on startup if configured
        if config.modbus.sync_on_startup:
            logger.info("Performing startup synchronization from Modbus bus...")
            try:
                modbus_manager.sync_from_bus()
                logger.info("Startup synchronization completed successfully")
            except Exception as e:
                logger.warning(f"Startup synchronization failed: {e}")
                # Continue anyway - we have fallback mechanisms
        
        return db_manager, modbus_manager
        
    except Exception as e:
        logger.exception(f"Failed to initialize managers: {e}")
        sys.exit(1)


def run_flask_app(app, config):
    """Run Flask app in a separate thread"""
    try:
        logger.info(f"Starting API server on {config.api.host}:{config.api.port}")
        app.run(
            host=config.api.host, 
            port=config.api.port, 
            debug=config.debug_mode,
            threaded=True,
            use_reloader=False  # Disable reloader in threaded mode
        )
    except Exception as e:
        logger.exception(f"Flask app error: {e}")
        shutdown_event.set()


async def run_async_main(config):
    """Run both Modbus server and Flask app"""
    global modbus_server_task
    
    try:
        # Initialize managers
        db_manager, modbus_manager = initialize_managers(config)
        
        # Create Flask app
        app = create_app(config)
        
        # Start Flask app in background thread
        flask_thread = threading.Thread(
            target=run_flask_app, 
            args=(app, config),
            daemon=True
        )
        flask_thread.start()
        logger.info("Flask API started in background thread")
        
        # Start Modbus server (this will run in the main asyncio loop)
        await run_modbus_server(config)
        
    except Exception as e:
        logger.exception(f"Async main error: {e}")
        shutdown_event.set()


def main():
    """Main application entry point"""
    global modbus_server_task
    
    try:
        # Load configuration
        config = get_config()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if config.debug_mode:
            logger.warning("Running in DEBUG mode")
        else:
            logger.info("Production mode: consider using Gunicorn for API")
            logger.info(f"Run: gunicorn --config gunicorn_config.py main:create_app()")
        
        # Run both servers
        asyncio.run(run_async_main(config))
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.exception(f"Application error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        logger.info("Cleaning up resources...")
        shutdown_event.set()
        close_modbus_manager()
        close_database_manager()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    main() 