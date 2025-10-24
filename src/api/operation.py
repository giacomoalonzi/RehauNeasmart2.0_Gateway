#!/usr/bin/env python3

import json
import logging
from flask import Blueprint, request, current_app
from models.operation_models import OperationMode, OperationState
from models.response_models import ErrorResponse
from utils.data_transformer import transform_api_response, apply_field_mappings
import const

_logger = logging.getLogger(__name__)

operation_bp = Blueprint('operation', __name__)


@operation_bp.route("/mode", methods=['POST', 'GET'])
def mode():
    """
    Mode endpoint for getting and updating operation mode.
    """
    # Get context from app config
    context = current_app.config['MODBUS_CONTEXT']
    slave_id = current_app.config['SLAVE_ID']
    
    if request.method == 'GET':
        try:
            mode_value = context[slave_id].getValues(
                const.READ_HR_CODE,
                const.GLOBAL_OP_MODE_ADDR,
                count=1
            )[0]
            
            # Transform mode value using mapping
            mode_name = const.MODE_MAPPING.get(mode_value, "unknown")
            mode_data = OperationMode(mode=mode_value)
            response_data = mode_data.to_dict()
            
            # Transform to camelCase for frontend
            response_data = transform_api_response(response_data, to_camel=True)
            response_data = apply_field_mappings(response_data, reverse=False)
            
            return current_app.response_class(
                response=json.dumps(response_data),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            _logger.error(f"Error getting mode data: {e}")
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
            
            # Transform payload from camelCase to snake_case
            transformed_payload = apply_field_mappings(payload, reverse=True)
            transformed_payload = transform_api_response(transformed_payload, to_camel=False)
            
            operation_mode = OperationMode.from_dict(transformed_payload)
            is_valid, error_msg = operation_mode.validate()
            if not is_valid:
                return current_app.response_class(
                    response=json.dumps(ErrorResponse(error_msg).to_dict()),
                    status=400,
                    mimetype='application/json'
                )
            
            if not isinstance(operation_mode.mode, list):
                operation_mode.mode = [operation_mode.mode]
            
            context[slave_id].setValues(
                const.WRITE_HR_CODE,
                const.GLOBAL_OP_MODE_ADDR,
                operation_mode.mode
            )
            
            return current_app.response_class(
                status=202,
                mimetype='application/json'
            )
            
        except Exception as e:
            _logger.error(f"Error updating mode data: {e}")
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Internal server error").to_dict()),
                status=500,
                mimetype='application/json'
            )


@operation_bp.route("/state", methods=['POST', 'GET'])
def state():
    """
    State endpoint for getting and updating operation state.
    """
    # Get context from app config
    context = current_app.config['MODBUS_CONTEXT']
    slave_id = current_app.config['SLAVE_ID']
    
    if request.method == 'GET':
        try:
            state_value = context[slave_id].getValues(
                const.READ_HR_CODE,
                const.GLOBAL_OP_STATE_ADDR,
                count=1
            )[0]
            
            # Transform state value using mapping
            state_name = const.STATE_MAPPING.get(state_value, "unknown")
            state_data = OperationState(state=state_value)
            response_data = state_data.to_dict()
            
            # Transform to camelCase for frontend
            response_data = transform_api_response(response_data, to_camel=True)
            response_data = apply_field_mappings(response_data, reverse=False)
            
            return current_app.response_class(
                response=json.dumps(response_data),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            _logger.error(f"Error getting state data: {e}")
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
            
            # Transform payload from camelCase to snake_case
            transformed_payload = apply_field_mappings(payload, reverse=True)
            transformed_payload = transform_api_response(transformed_payload, to_camel=False)
            
            operation_state = OperationState.from_dict(transformed_payload)
            is_valid, error_msg = operation_state.validate()
            if not is_valid:
                return current_app.response_class(
                    response=json.dumps(ErrorResponse(error_msg).to_dict()),
                    status=400,
                    mimetype='application/json'
                )
            
            if not isinstance(operation_state.state, list):
                operation_state.state = [operation_state.state]
            
            context[slave_id].setValues(
                const.WRITE_HR_CODE,
                const.GLOBAL_OP_STATE_ADDR,
                operation_state.state
            )
            
            return current_app.response_class(
                status=202,
                mimetype='application/json'
            )
            
        except Exception as e:
            _logger.error(f"Error updating state data: {e}")
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Internal server error").to_dict()),
                status=500,
                mimetype='application/json'
            )
