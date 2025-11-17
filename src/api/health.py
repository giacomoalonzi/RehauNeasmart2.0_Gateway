#!/usr/bin/env python3

import logging
from flask import Blueprint, current_app, jsonify

_logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


def _check_database_health():
    """Check database health status.
    
    Returns:
        tuple: (bool, str) - (is_healthy, debug_message)
    """
    try:
        from modbus_server import LockingPersistentDataBlock
        if LockingPersistentDataBlock.reg_dict is None:
            return False, "Database reg_dict is None - database not initialized"
        
        # Try to read a value to verify database is accessible
        try:
            _ = LockingPersistentDataBlock.reg_dict.get(0, 0)
            return True, "Database is accessible"
        except Exception as e:
            return False, f"Database read failed: {str(e)}"
    except Exception as e:
        return False, f"Database check failed: {str(e)}"


def _check_modbus_health():
    """Check Modbus connectivity health.
    
    Returns:
        tuple: (bool, str) - (is_healthy, debug_message)
    """
    try:
        context = current_app.config.get('MODBUS_CONTEXT')
        if context is None:
            return False, "MODBUS_CONTEXT is None - Modbus context not initialized in app config"
        
        # Check if context is initialized by trying to access it
        slave_id = current_app.config.get('SLAVE_ID', 240)
        if slave_id in context:
            try:
                # Just check if the context exists and is accessible
                _ = context[slave_id]
                return True, f"Modbus context accessible for slave_id {slave_id}"
            except Exception as e:
                return False, f"Modbus context access failed for slave_id {slave_id}: {str(e)}"
        return False, f"Slave ID {slave_id} not found in Modbus context"
    except Exception as e:
        return False, f"Modbus check failed: {str(e)}"


@health_bp.route("/health")
def get_health():
    """
    Health check endpoint.
    
    ---
    get:
      summary: Get system health status
      tags:
        - System
      description: Simple health check endpoint returning version and health status.
      responses:
        '200':
          description: System health status.
          content:
            application/json:
              schema:
                type: object
                properties:
                  version:
                    type: string
                    example: "2.0.0"
                  healthy:
                    type: boolean
                    example: true
    """
    try:
        # Check all components
        database_ok, database_msg = _check_database_health()
        modbus_ok, modbus_msg = _check_modbus_health()
        
        # System is healthy if both database and modbus are working
        healthy = database_ok and modbus_ok
        
        response = {
            "version": "2.0.0",
            "healthy": healthy
        }
        
        # Add debug information when system is unhealthy
        if not healthy:
            response["debug"] = {
                "database": {
                    "healthy": database_ok,
                    "message": database_msg
                },
                "modbus": {
                    "healthy": modbus_ok,
                    "message": modbus_msg
                }
            }
        
        status_code = 200 if healthy else 503
        return jsonify(response), status_code
    except Exception as e:
        _logger.error(f"Health check error: {e}", exc_info=True)
        return jsonify({
            "version": "2.0.0",
            "healthy": False,
            "debug": {
                "error": f"Health check exception: {str(e)}"
            }
        }), 503
