#!/usr/bin/env python3
"""
API endpoints for managing the global operation mode and state of the system.
"""

import logging
from flask import Blueprint, jsonify, request
from typing import Dict, Any, List

from modbus_manager import get_modbus_manager, ModbusException
from api.errors import handle_errors, ValidationError, APIError
import const

logger = logging.getLogger(__name__)

operation_bp = Blueprint('operation', __name__, url_prefix='/api/v1/operation')


def _validate_and_convert(value: str, mapping: Dict[str, int], value_type: str) -> int:
    """Generic helper to validate and convert a string value to its numeric counterpart."""
    if not isinstance(value, str):
        raise ValidationError(f"{value_type.capitalize()} must be a string.")

    numeric_value = mapping.get(value.lower())
    if numeric_value is None:
        valid_values: List[str] = list(mapping.keys())
        raise ValidationError(f"Invalid {value_type}: '{value}'. Must be one of {valid_values}")
    
    return numeric_value

def validate_and_convert_mode(mode: str) -> int:
    """Validate and convert descriptive mode to numeric mode using const.MODE_MAPPING_REVERSE."""
    return _validate_and_convert(mode, const.MODE_MAPPING_REVERSE, "mode")

def validate_and_convert_state(state: str) -> int:
    """Validate and convert descriptive state to numeric state using const.STATE_MAPPING_REVERSE."""
    return _validate_and_convert(state, const.STATE_MAPPING_REVERSE, "state")


@operation_bp.route('/mode', methods=['GET', 'POST'])
@handle_errors
def handle_operation_mode():
    """
    Get or set the global system operation mode.
    
    GET: Returns the current operation mode (e.g., "auto", "heating", "cooling").
    POST: Sets a new operation mode.
          Payload: {"mode": "auto"}
          Valid modes are: "auto", "heating", "cooling", "manual heating", "manual cooling".
    """
    modbus = get_modbus_manager()

    if request.method == 'GET':
        try:
            mode_value = modbus.read_register(const.GLOBAL_OP_MODE_ADDR)
            mode_str = const.MODE_MAPPING.get(mode_value, "unknown")
            return jsonify({"mode": mode_str}), 200
        except ModbusException as e:
            logger.error(f"Failed to get operation mode: {e}")
            raise APIError("Failed to communicate with Modbus device", 503) from e

    elif request.method == 'POST':
        if not request.is_json:
            raise ValidationError("Request must be JSON")
        
        payload = request.get_json()
        mode_str = payload.get("mode")

        if mode_str is None:
            raise ValidationError("Missing 'mode' key in payload")
        
        numeric_mode = validate_and_convert_mode(mode_str)
        
        try:
            modbus.write_register(const.GLOBAL_OP_MODE_ADDR, numeric_mode)
            return jsonify({'status': 'success', 'mode': mode_str}), 200
        except ModbusException as e:
            logger.error(f"Failed to set operation mode: {e}")
            raise APIError("Failed to communicate with Modbus device", 503) from e

@operation_bp.route('/state', methods=['GET', 'POST'])
@handle_errors
def handle_operation_state():
    """
    Get or set the global system operation state.
    
    GET: Returns the current operation state (e.g., "normal", "reduced", "standby").
    POST: Sets a new operation state.
          Payload: {"state": "normal"}
          Valid states are: "normal", "reduced", "standby", "scheduled", "party", "holiday".
    """
    modbus = get_modbus_manager()

    if request.method == 'GET':
        try:
            state_value = modbus.read_register(const.GLOBAL_OP_STATE_ADDR)
            state_str = const.STATE_MAPPING.get(state_value, "unknown")
            return jsonify({"state": state_str}), 200
        except ModbusException as e:
            logger.error(f"Failed to get operation state: {e}")
            raise APIError("Failed to communicate with Modbus device", 503) from e

    elif request.method == 'POST':
        if not request.is_json:
            raise ValidationError("Request must be JSON")
        
        payload = request.get_json()
        state_str = payload.get("state")

        if state_str is None:
            raise ValidationError("Missing 'state' key in payload")
        
        numeric_state = validate_and_convert_state(state_str)
        
        try:
            modbus.write_register(const.GLOBAL_OP_STATE_ADDR, numeric_state)
            return jsonify({'status': 'success', 'state': state_str}), 200
        except ModbusException as e:
            logger.error(f"Failed to set operation state: {e}")
            raise APIError("Failed to communicate with Modbus device", 503) from e 