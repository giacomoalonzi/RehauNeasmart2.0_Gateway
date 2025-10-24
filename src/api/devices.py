#!/usr/bin/env python3

import json
import logging
from flask import Blueprint, current_app
from models.response_models import ErrorResponse
from services.device_service import DeviceService

_logger = logging.getLogger(__name__)

devices_bp = Blueprint('devices', __name__)


@devices_bp.route("/dehumidifiers/<int:dehumidifier_id>", methods=['GET'])
def get_dehumidifier(dehumidifier_id=None):
    """
    Dehumidifier endpoint for getting dehumidifier data.
    
    Args:
        dehumidifier_id (int): Dehumidifier ID (1-9)
    """
    # Get services from app context
    context = current_app.config['MODBUS_CONTEXT']
    slave_id = current_app.config['SLAVE_ID']
    device_service = DeviceService(context, slave_id)
    
    # Validate parameters
    is_valid, error_msg = device_service.validate_dehumidifier_id(dehumidifier_id)
    if not is_valid:
        return current_app.response_class(
            response=json.dumps(ErrorResponse(error_msg).to_dict()),
            status=400,
            mimetype='application/json'
        )
    
    try:
        dehumidifier_data = device_service.get_dehumidifier_data(dehumidifier_id)
        return current_app.response_class(
            response=json.dumps(dehumidifier_data.to_dict()),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        _logger.error(f"Error getting dehumidifier data: {e}")
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json'
        )


@devices_bp.route("/pumps/<int:pump_id>", methods=['GET'])
def get_extra_pumps(pump_id=None):
    """
    Pump endpoint for getting pump data.
    
    Args:
        pump_id (int): Pump ID (1-5)
    """
    # Get services from app context
    context = current_app.config['MODBUS_CONTEXT']
    slave_id = current_app.config['SLAVE_ID']
    device_service = DeviceService(context, slave_id)
    
    # Validate parameters
    is_valid, error_msg = device_service.validate_pump_id(pump_id)
    if not is_valid:
        return current_app.response_class(
            response=json.dumps(ErrorResponse(error_msg).to_dict()),
            status=400,
            mimetype='application/json'
        )
    
    try:
        pump_data = device_service.get_pump_data(pump_id)
        return current_app.response_class(
            response=json.dumps(pump_data.to_dict()),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        _logger.error(f"Error getting pump data: {e}")
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json'
        )
