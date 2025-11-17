#!/usr/bin/env python3

import logging
from flask import Blueprint, current_app, jsonify

_logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


def _check_database_health():
    """Check database health status."""
    try:
        import database
        LockingPersistentDataBlock = database.LockingPersistentDataBlock
        if LockingPersistentDataBlock.reg_dict is None:
            return False
        
        # Try to read a value to verify database is accessible
        try:
            _ = LockingPersistentDataBlock.reg_dict.get(0, 0)
            return True
        except Exception:
            return False
    except Exception:
        return False


def _check_modbus_health():
    """Check Modbus connectivity health."""
    try:
        context = current_app.config.get('MODBUS_CONTEXT')
        if context is None:
            return False
        
        # Check if context is initialized by trying to access it
        slave_id = current_app.config.get('SLAVE_ID', 240)
        if slave_id in context:
            try:
                # Just check if the context exists and is accessible
                _ = context[slave_id]
                return True
            except Exception:
                return False
        return False
    except Exception:
        return False


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
        database_ok = _check_database_health()
        modbus_ok = _check_modbus_health()
        
        # System is healthy if both database and modbus are working
        healthy = database_ok and modbus_ok
        
        response = {
            "version": "2.0.0",
            "healthy": healthy
        }
        
        status_code = 200 if healthy else 503
        return jsonify(response), status_code
    except Exception as e:
        _logger.error(f"Health check error: {e}", exc_info=True)
        return jsonify({
            "version": "2.0.0",
            "healthy": False
        }), 503
