#!/usr/bin/env python3
"""
API endpoint for extra pumps.

NOTE: This endpoint is currently a placeholder and is not fully tested.
My home system does not have extra pumps configured, so this implementation
is based on the specification and requires real-world validation.
"""

import logging
from flask import Blueprint, jsonify

from modbus_manager import get_modbus_manager
from api.zones import handle_errors, ValidationError
import const

logger = logging.getLogger(__name__)

pumps_bp = Blueprint('pumps', __name__, url_prefix='/api/v1/pumps')

@pumps_bp.route('/<int:pump_id>', methods=['GET'])
@handle_errors
def get_pump(pump_id: int):
    """Get extra pump status."""
    if not 1 <= pump_id <= 5:
        raise ValidationError(f"Invalid pump ID: {pump_id}. Must be between 1 and 5.")

    modbus = get_modbus_manager()
    
    pump_state = modbus.read_register(
        pump_id + const.EXTRA_PUMPS_ADDR_OFFSET
    )
    
    data = {
        "pump_id": pump_id,
        "state": pump_state
    }
    
    return jsonify(data), 200 