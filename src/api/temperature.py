#!/usr/bin/env python3
"""
API endpoint for outside temperature.
"""

import logging
from flask import Blueprint, jsonify

from modbus_manager import get_modbus_manager, ModbusException
from api.errors import handle_errors
from api.zones import format_temperature
from config import get_config
import dpt_9001
import const

logger = logging.getLogger(__name__)

temperature_bp = Blueprint('temperature', __name__, url_prefix='/api/v1/temperature')

@temperature_bp.route('/outside', methods=['GET'])
@handle_errors
def get_outside_temperature():
    """
    Get the current outside and filtered outside temperatures.

    This endpoint reads the latest temperature data from the Modbus device,
    which is typically provided by an external sensor connected to the system.

    Returns:
        JSON object with temperature readings.
        Example:
        {
          "outside_temperature": {
            "value": 15.5,
            "unit": "°C"
          },
          "filtered_outside_temperature": {
            "value": 15.2,
            "unit": "°C"
          }
        }
        
    Raises:
        APIError (503): If communication with the Modbus device fails.
    """
    modbus = get_modbus_manager()
    config = get_config()

    outside_temp_raw = modbus.read_register(const.OUTSIDE_TEMPERATURE_ADDR)
    filtered_temp_raw = modbus.read_register(const.FILTERED_OUTSIDE_TEMPERATURE_ADDR)

    outside_temp = dpt_9001.unpack_dpt9001(outside_temp_raw)
    filtered_temp = dpt_9001.unpack_dpt9001(filtered_temp_raw)

    data = {
        "outside_temperature": format_temperature(outside_temp, config.api) if outside_temp is not None else None,
        "filtered_outside_temperature": format_temperature(filtered_temp, config.api) if filtered_temp is not None else None
    }

    return jsonify(data), 200 