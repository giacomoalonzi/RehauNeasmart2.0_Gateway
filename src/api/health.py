#!/usr/bin/env python3
"""
API endpoint for health checks.
"""

import logging
from flask import Blueprint, jsonify
from config import get_config
from database import get_database_manager
from modbus_manager import get_modbus_manager

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__, url_prefix='/api/v1')

@health_bp.route("/health")
def get_health():
    """Enhanced health check endpoint"""
    try:
        config = get_config()
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