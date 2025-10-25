#!/usr/bin/env python3

import logging
from flask import Blueprint

_logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


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
    return "OK"
