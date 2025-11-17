#!/usr/bin/env python3

import json
import logging
import os
from flask import Blueprint, current_app, jsonify

_logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


def _check_database_health():
    """Check database health status."""
    try:
        import database
        LockingPersistentDataBlock = database.LockingPersistentDataBlock
        if LockingPersistentDataBlock.reg_dict is None:
            return {
                "healthy": False,
                "type": "SQLite",
                "details": "Database not initialized"
            }
        
        # Try to read a value to verify database is accessible
        try:
            _ = LockingPersistentDataBlock.reg_dict.get(0, 0)
            return {
                "healthy": True,
                "type": "SQLite",
                "details": "Connected"
            }
        except Exception as e:
            return {
                "healthy": False,
                "type": "SQLite",
                "details": f"Database access error: {str(e)}"
            }
    except Exception as e:
        return {
            "healthy": False,
            "type": "Unknown",
            "details": f"Database check failed: {str(e)}"
        }


def _check_modbus_health():
    """Check Modbus connectivity health."""
    try:
        context = current_app.config.get('MODBUS_CONTEXT')
        if context is None:
            return {
                "healthy": False,
                "circuit_breaker": {
                    "state": "open",
                    "failures": 0
                }
            }
        
        # Check if context is initialized by trying to access it
        slave_id = current_app.config.get('SLAVE_ID', 240)
        if slave_id in context:
            # Try a simple read to verify connectivity
            try:
                # Just check if the context exists and is accessible
                _ = context[slave_id]
                return {
                    "healthy": True,
                    "circuit_breaker": {
                        "state": "closed",
                        "failures": 0
                    }
                }
            except Exception as e:
                return {
                    "healthy": False,
                    "circuit_breaker": {
                        "state": "open",
                        "failures": 1
                    }
                }
        else:
            return {
                "healthy": False,
                "circuit_breaker": {
                    "state": "open",
                    "failures": 0
                }
            }
    except Exception as e:
        _logger.error(f"Modbus health check failed: {e}")
        return {
            "healthy": False,
            "circuit_breaker": {
                "state": "open",
                "failures": 0
            }
        }


def _get_configuration():
    """Get current configuration."""
    try:
        config = current_app.config.get('SERVER_CONFIG')
        if config is None:
            return {
                "server_type": "unknown",
                "api_auth_enabled": False,
                "fallback_enabled": True
            }
        
        return {
            "server_type": getattr(config, 'server_type', 'unknown'),
            "api_auth_enabled": os.getenv('NEASMART_API_ENABLE_AUTH', 'false').lower() == 'true',
            "fallback_enabled": True  # Database fallback is always enabled
        }
    except Exception as e:
        _logger.error(f"Configuration check failed: {e}")
        return {
            "server_type": "unknown",
            "api_auth_enabled": False,
            "fallback_enabled": True
        }


@health_bp.route("/health")
def get_health():
    """
    Health check endpoint.
    
    ---
    get:
      summary: Get system health status
      tags:
        - System
      description: Provides a detailed health check of the gateway, including database and Modbus connectivity.
      responses:
        '200':
          description: System is healthy or degraded.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'
        '503':
          description: System is unhealthy.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'
    """
    try:
        # Check all components
        database_health = _check_database_health()
        modbus_health = _check_modbus_health()
        configuration = _get_configuration()
        
        # Determine overall status
        database_ok = database_health.get("healthy", False)
        modbus_ok = modbus_health.get("healthy", False)
        
        if database_ok and modbus_ok:
            status = "healthy"
            status_code = 200
        elif database_ok or modbus_ok:
            status = "degraded"
            status_code = 200
        else:
            status = "unhealthy"
            status_code = 503
        
        response = {
            "status": status,
            "version": "2.1.0",
            "database": database_health,
            "modbus": modbus_health,
            "configuration": configuration
        }
        
        return jsonify(response), status_code
    except Exception as e:
        _logger.error(f"Health check error: {e}", exc_info=True)
        return jsonify({
            "status": "unhealthy",
            "version": "2.1.0",
            "database": {"healthy": False, "type": "Unknown", "details": str(e)},
            "modbus": {"healthy": False, "circuit_breaker": {"state": "unknown", "failures": 0}},
            "configuration": {"server_type": "unknown", "api_auth_enabled": False, "fallback_enabled": True}
        }), 503
