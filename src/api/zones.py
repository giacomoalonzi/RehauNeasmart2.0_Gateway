#!/usr/bin/env python3

import json
import logging
from flask import Blueprint, request, current_app
from models.zone_models import ZoneRequest
from models.response_models import ErrorResponse
from services.zone_service import ZoneService

_logger = logging.getLogger(__name__)

zones_bp = Blueprint('zones', __name__)


@zones_bp.route("/zones/<int:base_id>/<int:zone_id>", methods=['POST', 'GET'])
def zone(base_id=None, zone_id=None):
    """
    Zone endpoint for getting and updating zone data.
    
    Args:
        base_id (int): Base ID (1-4)
        zone_id (int): Zone ID (1-12)
    """
    # Get services from app context
    context = current_app.config['MODBUS_CONTEXT']
    slave_id = current_app.config['SLAVE_ID']
    zone_service = ZoneService(context, slave_id)
    
    # Validate parameters
    is_valid, error_msg = zone_service.validate_zone_params(base_id, zone_id)
    if not is_valid:
        return current_app.response_class(
            response=json.dumps(ErrorResponse(error_msg).to_dict()),
            status=400,
            mimetype='application/json'
        )
    
    if request.method == 'GET':
        try:
            zone_data = zone_service.get_zone_data(base_id, zone_id)
            return current_app.response_class(
                response=json.dumps(zone_data.to_dict()),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            _logger.error(f"Error getting zone data: {e}")
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Internal server error").to_dict()),
                status=500,
                mimetype='application/json'
            )
    
    elif request.method == 'POST':
        try:
            payload = request.json
            if not payload:
                return current_app.response_class(
                    response=json.dumps(ErrorResponse("Invalid JSON payload").to_dict()),
                    status=400,
                    mimetype='application/json'
                )
            
            zone_request = ZoneRequest.from_dict(payload)
            is_valid, error_msg = zone_request.validate()
            if not is_valid:
                return current_app.response_class(
                    response=json.dumps(ErrorResponse(error_msg).to_dict()),
                    status=400,
                    mimetype='application/json'
                )
            
            success, message, dpt_9001_setpoint = zone_service.update_zone_data(
                base_id, zone_id, zone_request
            )
            
            response_data = {"message": message}
            if dpt_9001_setpoint is not None:
                response_data["dpt_9001_setpoint"] = dpt_9001_setpoint
            
            return current_app.response_class(
                response=json.dumps(response_data),
                status=202,
                mimetype='application/json'
            )
            
        except Exception as e:
            _logger.error(f"Error updating zone data: {e}")
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Internal server error").to_dict()),
                status=500,
                mimetype='application/json'
            )
