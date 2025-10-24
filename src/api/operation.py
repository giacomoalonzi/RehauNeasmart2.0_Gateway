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
    """Legacy mode endpoint returning integer payloads."""
    service = _get_service()

    if request.method == 'GET':
        try:
            mode_value = service.get_mode()
            operation_mode = OperationMode(mode=mode_value)
            response_data = operation_mode.to_dict()
            response_data = transform_api_response(response_data, to_camel=True)
            response_data = apply_field_mappings(response_data, reverse=False)
            return current_app.response_class(
                response=json.dumps(response_data),
                status=200,
                mimetype='application/json',
            )
        except Exception as exc:
            _logger.error("Error getting mode data: %s", exc)
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
    """Legacy state endpoint returning integer payloads."""
    service = _get_service()

    if request.method == 'GET':
        try:
            state_value = service.get_state()
            operation_state = OperationState(state=state_value)
            response_data = operation_state.to_dict()
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
    service = _get_service()
    try:
        readable_mode = service.get_mode_name()
        payload = {'mode': readable_mode}
        payload = transform_api_response(payload, to_camel=True, allowed_keys={'mode'})
        return current_app.response_class(
            response=json.dumps(payload),
            status=200,
            mimetype='application/json',
        )
    except Exception as exc:
        _logger.error("Error getting mode data (v2): %s", exc)
        return current_app.response_class(
            response=json.dumps(ErrorResponse("Internal server error").to_dict()),
            status=500,
            mimetype='application/json',
        )


@operation_v2_bp.route("/operation/mode", methods=['POST'])
def mode_v2_post():
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
