#!/usr/bin/env python3

import json
import logging
from flask import Blueprint, current_app
from models.response_models import ErrorResponse
from services.temperature_service import TemperatureService

_logger = logging.getLogger(__name__)

temperature_bp = Blueprint('temperature', __name__)


@temperature_bp.route("/outsidetemperature", methods=['GET'])
def get_outside_temp():
    """
    Outside temperature endpoint for getting temperature data.
    """
    # Get services from app context
    context = current_app.config['MODBUS_CONTEXT']
    slave_id = current_app.config['SLAVE_ID']
    temperature_service = TemperatureService(context, slave_id)
    
    try:
        temperature_data = temperature_service.get_outside_temperature_data()
        return current_app.response_class(
            response=json.dumps(temperature_data.to_dict()),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        _logger.error(f"Error getting temperature data: {e}")
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json'
        )
