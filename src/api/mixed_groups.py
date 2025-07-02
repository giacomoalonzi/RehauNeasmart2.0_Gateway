#!/usr/bin/env python3
"""
API endpoint for mixed groups.

NOTE: This endpoint is currently a placeholder and is not fully tested.
I do not have a mixed group setup in my home system (which is heating only),
so this code is based on the specification but requires real-world validation.
"""

import logging
from flask import Blueprint, jsonify

from modbus_manager import get_modbus_manager
from api.zones import handle_errors, format_temperature, ValidationError
from config import get_config
import dpt_9001
import const

logger = logging.getLogger(__name__)

mixed_groups_bp = Blueprint('mixed_groups', __name__, url_prefix='/api/v1/mixed-groups')

@mixed_groups_bp.route('/<int:group_id>', methods=['GET'])
@handle_errors
def get_mixed_group(group_id: int):
    """Get mixed group information."""
    if not 1 <= group_id <= 3:
        raise ValidationError(f"Invalid mixed group ID: {group_id}. Must be between 1 and 3.")

    modbus = get_modbus_manager()
    config = get_config()

    base_reg = const.MIXEDGROUP_BASE_REG[group_id]

    pump_state = modbus.read_register(base_reg + const.MIXEDGROUP_PUMP_STATE_OFFSET)
    valve_opening = modbus.read_register(base_reg + const.MIXEDGROUP_VALVE_OPENING_OFFSET)
    flow_temp_raw = modbus.read_register(base_reg + const.MIXEDGROUP_FLOW_TEMP_OFFSET)
    return_temp_raw = modbus.read_register(base_reg + const.MIXEDGROUP_RETURN_TEMP_OFFSET)

    flow_temp = dpt_9001.unpack_dpt9001(flow_temp_raw)
    return_temp = dpt_9001.unpack_dpt9001(return_temp_raw)

    data = {
        "group_id": group_id,
        "pump_state": pump_state,
        "mixing_valve_opening_percentage": valve_opening,
        "flow_temperature": format_temperature(flow_temp, config.api),
        "return_temperature": format_temperature(return_temp, config.api)
    }

    return jsonify(data), 200 