#!/usr/bin/env python3
"""
API endpoint for dehumidifiers.

NOTE: This endpoint is currently a placeholder and is not fully tested.
My home system does not include dehumidifiers, so this implementation is
based on the specification and requires real-world validation.
"""

import logging
from flask import Blueprint, jsonify

from modbus_manager import get_modbus_manager
from api.zones import handle_errors, ValidationError
import const

logger = logging.getLogger(__name__)

dehumidifiers_bp = Blueprint('dehumidifiers', __name__, url_prefix='/api/v1/dehumidifiers')

@dehumidifiers_bp.route('/<int:dehumidifier_id>', methods=['GET'])
@handle_errors
def get_dehumidifier(dehumidifier_id: int):
    """Get dehumidifier status."""
    if not 1 <= dehumidifier_id <= 9:
        raise ValidationError(f"Invalid dehumidifier ID: {dehumidifier_id}. Must be between 1 and 9.")

    modbus = get_modbus_manager()
    
    dehumidifier_state = modbus.read_register(
        dehumidifier_id + const.DEHUMIDIFIERS_ADDR_OFFSET
    )
    
    data = {
        "dehumidifier_id": dehumidifier_id,
        "state": dehumidifier_state
    }
    
    return jsonify(data), 200 