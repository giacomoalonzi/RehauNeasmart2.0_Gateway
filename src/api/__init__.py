#!/usr/bin/env python3

from flask import Blueprint

from .devices import devices_bp
from .health import health_bp
from .mixed_groups import mixed_groups_bp
from .notifications import notifications_bp
from .operation import legacy_operation_bp, operation_v2_bp
from .temperature import temperature_bp
from .zones import zones_bp


def register_blueprints(app):
    """Register API blueprints with versioned namespaces."""

    api_bp = Blueprint('api', __name__, url_prefix='/api')
    api_bp.register_blueprint(zones_bp)
    api_bp.register_blueprint(mixed_groups_bp)
    api_bp.register_blueprint(temperature_bp)
    api_bp.register_blueprint(notifications_bp)
    api_bp.register_blueprint(legacy_operation_bp)
    api_bp.register_blueprint(devices_bp)
    api_bp.register_blueprint(health_bp)

    api_v2_bp = Blueprint('api_v2', __name__, url_prefix='/api/v2')
    api_v2_bp.register_blueprint(operation_v2_bp)

    app.register_blueprint(api_bp)
    app.register_blueprint(api_v2_bp)
