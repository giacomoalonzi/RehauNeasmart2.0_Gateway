#!/usr/bin/env python3
"""
API endpoint for system notifications.
"""

import logging
from flask import Blueprint, jsonify

from modbus_manager import get_modbus_manager
from api.errors import handle_errors
import const

logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/v1/notifications')

@notifications_bp.route('/', methods=['GET'])
@handle_errors
def get_notifications():
    """
    Get the status of system-level notifications.

    This endpoint checks for active hints, warnings, or errors reported by
    the Nea Smart 2.0 system. These are boolean flags. For example, `true`
    for `warnings_present` indicates that one or more warnings are active.

    Returns:
        JSON object with notification statuses.
        Example:
        {
          "hints_present": false,
          "warnings_present": true,
          "errors_present": false
        }

    Raises:
        APIError (503): If communication with the Modbus device fails.
    """
    modbus = get_modbus_manager()
    
    data = {
        "hints_present": modbus.read_register(const.HINTS_PRESENT_ADDR) == 1,
        "warnings_present": modbus.read_register(const.WARNINGS_PRESENT_ADDR) == 1,
        "errors_present": modbus.read_register(const.ERRORS_PRESENT_ADDR) == 1
    }
    
    return jsonify(data), 200 