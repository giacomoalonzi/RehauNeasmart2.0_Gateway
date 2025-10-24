#!/usr/bin/env python3

import json
import logging
from flask import Blueprint, current_app
from models.response_models import ErrorResponse
from services.device_service import DeviceService

_logger = logging.getLogger(__name__)

mixed_groups_bp = Blueprint('mixed_groups', __name__)


@mixed_groups_bp.route("/mixedgroups/<int:group_id>", methods=['GET'])
def get_mixed_circuit(group_id=None):
    """
    Mixed group endpoint for getting mixed circuit data.
    
    Args:
        group_id (int): Group ID (1-3)
    """
    # Get services from app context
    context = current_app.config['MODBUS_CONTEXT']
    slave_id = current_app.config['SLAVE_ID']
    device_service = DeviceService(context, slave_id)
    
    # Validate parameters
    is_valid, error_msg = device_service.validate_mixed_group_id(group_id)
    if not is_valid:
        return current_app.response_class(
            response=json.dumps(ErrorResponse(error_msg).to_dict()),
            status=400,
            mimetype='application/json'
        )
    
    try:
        mixed_group_data = device_service.get_mixed_group_data(group_id)
        return current_app.response_class(
            response=json.dumps(mixed_group_data.to_dict()),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        _logger.error(f"Error getting mixed group data: {e}")
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json'
        )
