#!/usr/bin/env python3

import json
import logging
from flask import Blueprint, current_app, request

from models.operation_models import OperationMode, OperationState
from models.response_models import ErrorResponse
from services.operation_service import OperationService
from utils import state_converter
from utils.data_transformer import apply_field_mappings, transform_api_response

_logger = logging.getLogger(__name__)

legacy_operation_bp = Blueprint('legacy_operation', __name__)
operation_v2_bp = Blueprint('operation_v2', __name__)


def _get_service() -> OperationService:
    context = current_app.config['MODBUS_CONTEXT']
    slave_id = current_app.config['SLAVE_ID']
    return OperationService(context, slave_id)


@legacy_operation_bp.route("/mode", methods=['POST', 'GET'])
def mode():
    """
    Legacy mode endpoint returning human-readable payloads.
    
    ---
    get:
      summary: Get global operation mode
      tags:
        - Operation
      description: Retrieves the current global operation mode of the system (e.g., "auto", "heating", "cooling").
      responses:
        '200':
          description: Current operation mode.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OperationModeResponse'
        '503':
          $ref: '#/components/responses/ServiceUnavailable'
    post:
      summary: Set global operation mode
      tags:
        - Operation
      description: Sets a new global operation mode for the system.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OperationModeUpdateRequest'
      responses:
        '202':
          description: Mode update accepted.
        '400':
          $ref: '#/components/responses/BadRequest'
        '503':
          $ref: '#/components/responses/ServiceUnavailable'
    """
    service = _get_service()

    if request.method == 'GET':
        try:
            mode_value = service.get_mode()
            
            # Validate mode value before processing
            if mode_value < 1 or mode_value > 5:
                _logger.warning(
                    "Invalid mode value received: %s (type: %s). "
                    "Expected range: 1-5. This may indicate uninitialized system or Modbus communication issue.",
                    mode_value,
                    type(mode_value).__name__
                )
                error_details = {
                    "raw_value": mode_value,
                    "value_type": type(mode_value).__name__,
                    "expected_range": "1-5",
                    "valid_modes": {
                        1: "auto",
                        2: "heating",
                        3: "cooling",
                        4: "manual heating",
                        5: "manual cooling"
                    }
                }
                return current_app.response_class(
                    response=json.dumps(ErrorResponse(
                        f"System returned invalid mode value: {mode_value} (expected 1-5). "
                        f"This may indicate the system is uninitialized or there is a Modbus communication issue."
                    ).to_dict() | {"debug_info": error_details}),
                    status=503,
                    mimetype='application/json',
                )
            
            operation_mode = OperationMode(mode=mode_value)
            response_data = operation_mode.to_dict(readable=True)
            response_data = transform_api_response(response_data, to_camel=True)
            response_data = apply_field_mappings(response_data, reverse=False)
            return current_app.response_class(
                response=json.dumps(response_data),
                status=200,
                mimetype='application/json',
            )
        except ValueError as exc:
            # Handle ValueError from mode_to_name conversion (e.g., mode value outside valid range)
            _logger.warning("Invalid mode value from system: %s", exc, exc_info=True)
            return current_app.response_class(
                response=json.dumps(ErrorResponse(f"System returned invalid mode value: {str(exc)}").to_dict()),
                status=503,
                mimetype='application/json',
            )
        except Exception as exc:
            _logger.error("Error getting mode data: %s", exc, exc_info=True)
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Internal server error").to_dict()),
                status=500,
                mimetype='application/json',
            )

    try:
        payload = request.json
        if not payload:
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Invalid JSON payload").to_dict()),
                status=400,
                mimetype='application/json',
            )

        transformed_payload = apply_field_mappings(payload, reverse=True)
        operation_mode = OperationMode.from_dict(transformed_payload)
        is_valid, error_msg = operation_mode.validate()
        if not is_valid:
            return current_app.response_class(
                response=json.dumps(ErrorResponse(error_msg).to_dict()),
                status=400,
                mimetype='application/json',
            )

        service.set_mode(operation_mode.mode)
        return current_app.response_class(status=202, mimetype='application/json')
    except ValueError as exc:
        _logger.warning("Validation failed for mode update: %s", exc)
        return current_app.response_class(
            response=json.dumps(ErrorResponse(str(exc)).to_dict()),
            status=400,
            mimetype='application/json',
        )
    except Exception as exc:
        _logger.error("Error updating mode data: %s", exc)
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json',
        )


@legacy_operation_bp.route("/state", methods=['POST', 'GET'])
def state():
    """
    Legacy state endpoint returning human-readable payloads.
    
    ---
    get:
      summary: Get global operation state
      tags:
        - Operation
      description: Retrieves the current global operation state of the system (e.g., "presence", "standby").
      responses:
        '200':
          description: Current operation state.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OperationStateResponse'
        '503':
          $ref: '#/components/responses/ServiceUnavailable'
    post:
      summary: Set global operation state
      tags:
        - Operation
      description: Sets a new global operation state for the system.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OperationStateUpdateRequest'
      responses:
        '200':
          description: State update accepted.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OperationStateUpdateResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '503':
          $ref: '#/components/responses/ServiceUnavailable'
    """
    service = _get_service()

    if request.method == 'GET':
        try:
            state_value = service.get_state()
            operation_state = OperationState(state=state_value)
            response_data = operation_state.to_dict(readable=True)
            response_data = transform_api_response(response_data, to_camel=True)
            response_data = apply_field_mappings(response_data, reverse=False)
            return current_app.response_class(
                response=json.dumps(response_data),
                status=200,
                mimetype='application/json',
            )
        except Exception as exc:
            _logger.error("Error getting state data: %s", exc)
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Internal server error").to_dict()),
                status=500,
                mimetype='application/json',
            )

    try:
        payload = request.json
        if not payload:
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Invalid JSON payload").to_dict()),
                status=400,
                mimetype='application/json',
            )

        transformed_payload = apply_field_mappings(payload, reverse=True)
        operation_state = OperationState.from_dict(transformed_payload)
        is_valid, error_msg = operation_state.validate()
        if not is_valid:
            return current_app.response_class(
                response=json.dumps(ErrorResponse(error_msg).to_dict()),
                status=400,
                mimetype='application/json',
            )

        service.set_state(operation_state.state)
        return current_app.response_class(status=202, mimetype='application/json')
    except ValueError as exc:
        _logger.warning("Validation failed for state update: %s", exc)
        return current_app.response_class(
            response=json.dumps(ErrorResponse(str(exc)).to_dict()),
            status=400,
            mimetype='application/json',
        )
    except Exception as exc:
        _logger.error("Error updating state data: %s", exc)
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json',
        )


@operation_v2_bp.route("/operation/mode", methods=['GET'])
def mode_v2_get():
    """
    Get global operation mode (v2).
    
    ---
    get:
      summary: Get global operation mode
      tags:
        - Operation
      description: Retrieves the current global operation mode of the system (e.g., "auto", "heating", "cooling").
      responses:
        '200':
          description: Current operation mode.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OperationModeResponse'
        '503':
          $ref: '#/components/responses/ServiceUnavailable'
    """
    service = _get_service()
    try:
        # Get raw value first for debugging
        mode_value = service.get_mode()
        
        # Validate mode value before converting to name
        if mode_value < 1 or mode_value > 5:
            _logger.warning(
                "Invalid mode value received (v2): %s (type: %s). "
                "Expected range: 1-5. This may indicate uninitialized system or Modbus communication issue.",
                mode_value,
                type(mode_value).__name__
            )
            error_details = {
                "raw_value": mode_value,
                "value_type": type(mode_value).__name__,
                "expected_range": "1-5",
                "valid_modes": {
                    1: "auto",
                    2: "heating",
                    3: "cooling",
                    4: "manual heating",
                    5: "manual cooling"
                }
            }
            return current_app.response_class(
                response=json.dumps(ErrorResponse(
                    f"System returned invalid mode value: {mode_value} (expected 1-5). "
                    f"This may indicate the system is uninitialized or there is a Modbus communication issue."
                ).to_dict() | {"debug_info": error_details}),
                status=503,
                mimetype='application/json',
            )
        
        readable_mode = service.get_mode_name()
        payload = {'mode': readable_mode}
        payload = transform_api_response(payload, to_camel=True, allowed_keys={'mode'})
        return current_app.response_class(
            response=json.dumps(payload),
            status=200,
            mimetype='application/json',
        )
    except ValueError as exc:
        # Handle ValueError from mode_to_name conversion (e.g., mode value outside valid range)
        _logger.warning("Invalid mode value from system (v2): %s", exc, exc_info=True)
        return current_app.response_class(
            response=json.dumps(ErrorResponse(f"System returned invalid mode value: {str(exc)}").to_dict()),
            status=503,
            mimetype='application/json',
        )
    except Exception as exc:
        _logger.error("Error getting mode data (v2): %s", exc, exc_info=True)
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json',
        )


@operation_v2_bp.route("/operation/mode", methods=['POST'])
def mode_v2_post():
    """
    Set global operation mode (v2).
    
    ---
    post:
      summary: Set global operation mode
      tags:
        - Operation
      description: Sets a new global operation mode for the system.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OperationModeUpdateRequest'
      responses:
        '202':
          description: Mode update accepted.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OperationModeUpdateResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '503':
          $ref: '#/components/responses/ServiceUnavailable'
    """
    service = _get_service()
    try:
        payload = request.json
        if not payload:
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Invalid JSON payload").to_dict()),
                status=400,
                mimetype='application/json',
            )

        transformed_payload = apply_field_mappings(payload, reverse=True)
        operation_mode = OperationMode.from_dict(transformed_payload)
        is_valid, error_msg = operation_mode.validate()
        if not is_valid:
            return current_app.response_class(
                response=json.dumps(ErrorResponse(error_msg).to_dict()),
                status=400,
                mimetype='application/json',
            )

        service.set_mode(operation_mode.mode)
        response_payload = OperationMode(mode=operation_mode.mode).to_dict(readable=True)
        response_payload = transform_api_response(response_payload, to_camel=True, allowed_keys={'mode'})
        return current_app.response_class(
            response=json.dumps(response_payload),
            status=202,
            mimetype='application/json',
        )
    except ValueError as exc:
        _logger.warning("Validation failed for mode update (v2): %s", exc)
        return current_app.response_class(
            response=json.dumps(ErrorResponse(str(exc)).to_dict()),
            status=400,
            mimetype='application/json',
        )
    except Exception as exc:
        _logger.error("Error updating mode data (v2): %s", exc)
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json',
        )


@operation_v2_bp.route("/operation/state", methods=['GET'])
def state_v2_get():
    service = _get_service()
    try:
        readable_state = service.get_state_name()
        payload = {'state': readable_state}
        payload = transform_api_response(payload, to_camel=True, allowed_keys={'state'})
        return current_app.response_class(
            response=json.dumps(payload),
            status=200,
            mimetype='application/json',
        )
    except Exception as exc:
        _logger.error("Error getting state data (v2): %s", exc)
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json',
        )


@operation_v2_bp.route("/operation/state", methods=['POST'])
def state_v2_post():
    service = _get_service()
    try:
        payload = request.json
        if not payload:
            return current_app.response_class(
                response=json.dumps(ErrorResponse("Invalid JSON payload").to_dict()),
                status=400,
                mimetype='application/json',
            )

        transformed_payload = apply_field_mappings(payload, reverse=True)
        operation_state = OperationState.from_dict(transformed_payload)
        is_valid, error_msg = operation_state.validate()
        if not is_valid:
            return current_app.response_class(
                response=json.dumps(ErrorResponse(error_msg).to_dict()),
                status=400,
                mimetype='application/json',
            )

        service.set_state(operation_state.state)
        response_payload = OperationState(state=operation_state.state).to_dict(readable=True)
        response_payload = transform_api_response(response_payload, to_camel=True, allowed_keys={'state'})
        return current_app.response_class(
            response=json.dumps(response_payload),
            status=202,
            mimetype='application/json',
        )
    except ValueError as exc:
        _logger.warning("Validation failed for state update (v2): %s", exc)
        return current_app.response_class(
            response=json.dumps(ErrorResponse(str(exc)).to_dict()),
            status=400,
            mimetype='application/json',
        )
    except Exception as exc:
        _logger.error("Error updating state data (v2): %s", exc)
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json',
        )
