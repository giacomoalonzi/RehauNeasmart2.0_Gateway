#!/usr/bin/env python3

from flask import Blueprint

# Create main API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import all API modules
from .zones import zones_bp
from .mixed_groups import mixed_groups_bp
from .temperature import temperature_bp
from .notifications import notifications_bp
from .operation import operation_bp
from .devices import devices_bp
from .health import health_bp

def register_blueprints(app):
    """
    Register all API blueprints with the Flask application.
    
    Args:
        app (Flask): Flask application instance
    """
    # Register individual blueprints
    api_bp.register_blueprint(zones_bp)
    api_bp.register_blueprint(mixed_groups_bp)
    api_bp.register_blueprint(temperature_bp)
    api_bp.register_blueprint(notifications_bp)
    api_bp.register_blueprint(operation_bp)
    api_bp.register_blueprint(devices_bp)
    api_bp.register_blueprint(health_bp)
    
    # Register main API blueprint
    app.register_blueprint(api_bp)
