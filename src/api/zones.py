#!/usr/bin/env python3
"""
Zones API endpoints for Rehau Neasmart Gateway.
Handles zone operations with robust error handling.
"""

import logging
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify
from functools import wraps

from modbus_manager import get_modbus_manager, ModbusException
import dpt_9001
import const
from config import get_config

logger = logging.getLogger(__name__)

zones_bp = Blueprint('zones', __name__, url_prefix='/api/v1/zones')


class APIError(Exception):
    """Base API error"""
    status_code = 500
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        return {'error': self.message, 'status': self.status_code}


class ValidationError(APIError):
    """Validation error"""
    status_code = 400


class NotFoundError(APIError):
    """Resource not found error"""
    status_code = 404


def handle_errors(f):
    """Decorator to handle API errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            logger.warning(f"API error in {f.__name__}: {e.message}")
            return jsonify(e.to_dict()), e.status_code
        except ModbusException as e:
            logger.error(f"Modbus error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Communication error with Modbus device',
                'details': str(e),
                'status': 503
            }), 503
        except Exception as e:
            logger.exception(f"Unexpected error in {f.__name__}")
            return jsonify({
                'error': 'Internal server error',
                'status': 500
            }), 500
    
    return decorated_function


def validate_base_id(base_id: int) -> None:
    """Validate base ID"""
    if not 1 <= base_id <= 4:
        raise ValidationError(f"Invalid base ID: {base_id}. Must be between 1 and 4")


def validate_zone_id(zone_id: int) -> None:
    """Validate zone ID"""
    if not 1 <= zone_id <= 12:
        raise ValidationError(f"Invalid zone ID: {zone_id}. Must be between 1 and 12")


def validate_state(state: int) -> None:
    """Validate zone state"""
    if not 1 <= state <= 6:
        raise ValidationError(f"Invalid state: {state}. Must be between 1 and 6")


def validate_setpoint(setpoint: float) -> None:
    """Validate temperature setpoint"""
    if not 5.0 <= setpoint <= 40.0:
        raise ValidationError(f"Invalid setpoint: {setpoint}. Must be between 5.0 and 40.0°C")


def calculate_zone_address(base_id: int, zone_id: int) -> int:
    """Calculate zone address from base and zone IDs"""
    return (base_id - 1) * const.NEASMART_BASE_SLAVE_ADDR + zone_id * const.BASE_ZONE_ID


@zones_bp.route('/<int:base_id>/<int:zone_id>', methods=['GET'])
@handle_errors
def get_zone(base_id: int, zone_id: int):
    """Get zone information"""
    # Validate inputs
    validate_base_id(base_id)
    validate_zone_id(zone_id)
    # Check slave_id
    config = get_config()
    if config.modbus.slave_id != 240:
        raise ValidationError(f"Configured slave_id is {config.modbus.slave_id}, only slave_id=240 is supported.")
    # Calculate address
    zone_addr = calculate_zone_address(base_id, zone_id)
    
    # Get Modbus manager
    modbus = get_modbus_manager()
    
    # Read zone data
    try:
        state = modbus.read_register(zone_addr)
        setpoint_raw = modbus.read_register(zone_addr + const.ZONE_SETPOINT_ADDR_OFFSET)
        temperature_raw = modbus.read_register(zone_addr + const.ZONE_TEMP_ADDR_OFFSET)
        humidity = modbus.read_register(zone_addr + const.ZONE_RH_ADDR_OFFSET)
        
        # Decode DPT 9.001 values
        setpoint = dpt_9001.unpack_dpt9001(setpoint_raw)
        temperature = dpt_9001.unpack_dpt9001(temperature_raw)
        
    except Exception as e:
        logger.error(f"Failed to read zone {base_id}/{zone_id}: {e}")
        raise ModbusException(f"Failed to read zone data: {str(e)}")
    
    # Prepare response
    response_data = {
        'base_id': base_id,
        'zone_id': zone_id,
        'state': state,
        'setpoint': round(setpoint, 1),
        'temperature': round(temperature, 1),
        'relative_humidity': humidity,
        'address': zone_addr
    }
    
    return jsonify(response_data), 200


@zones_bp.route('/<int:base_id>/<int:zone_id>', methods=['POST'])
@handle_errors
def update_zone(base_id: int, zone_id: int):
    """Update zone parameters"""
    # Validate inputs
    validate_base_id(base_id)
    validate_zone_id(zone_id)
    # Check slave_id
    config = get_config()
    if config.modbus.slave_id != 240:
        raise ValidationError(f"Configured slave_id is {config.modbus.slave_id}, only slave_id=240 is supported.")
    
    # Parse request body
    if not request.is_json:
        raise ValidationError("Request must be JSON")
    
    data = request.get_json()
    state = data.get('state')
    setpoint = data.get('setpoint')
    
    # Validate that at least one parameter is provided
    if state is None and setpoint is None:
        raise ValidationError("At least one of 'state' or 'setpoint' must be provided")
    
    # Calculate address
    zone_addr = calculate_zone_address(base_id, zone_id)
    
    # Get Modbus manager
    modbus = get_modbus_manager()
    
    response_data = {
        'base_id': base_id,
        'zone_id': zone_id,
        'updated': {}
    }
    
    # Update state if provided
    if state is not None:
        if not isinstance(state, int):
            raise ValidationError("State must be an integer")
        validate_state(state)
        
        try:
            modbus.write_register(zone_addr, state)
            response_data['updated']['state'] = state
        except Exception as e:
            logger.error(f"Failed to update zone state: {e}")
            raise ModbusException(f"Failed to update state: {str(e)}")
    
    # Update setpoint if provided
    if setpoint is not None:
        if not isinstance(setpoint, (int, float)):
            raise ValidationError("Setpoint must be a number")
        validate_setpoint(float(setpoint))
        
        try:
            # Encode to DPT 9.001
            encoded_setpoint = dpt_9001.pack_dpt9001(float(setpoint))
            modbus.write_register(zone_addr + const.ZONE_SETPOINT_ADDR_OFFSET, encoded_setpoint)
            response_data['updated']['setpoint'] = float(setpoint)
            response_data['updated']['setpoint_encoded'] = encoded_setpoint
        except Exception as e:
            logger.error(f"Failed to update zone setpoint: {e}")
            raise ModbusException(f"Failed to update setpoint: {str(e)}")
    
    return jsonify(response_data), 200


@zones_bp.route('/', methods=['GET'])
@handle_errors
def list_zones():
    """List all zones with their current status"""
    # Get query parameters
    base_id = request.args.get('base_id', type=int)
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    
    # Validate base_id if provided
    if base_id is not None:
        validate_base_id(base_id)
        base_ids = [base_id]
    else:
        base_ids = range(1, 5)  # All base IDs
    
    # Get Modbus manager
    modbus = get_modbus_manager()
    
    zones = []
    
    for bid in base_ids:
        for zid in range(1, 13):  # All zone IDs
            try:
                zone_addr = calculate_zone_address(bid, zid)
                
                # Read zone state first to check if active
                state = modbus.read_register(zone_addr)
                
                # Skip inactive zones if requested
                if not include_inactive and state == 0:
                    continue
                
                # Read other values
                setpoint_raw = modbus.read_register(zone_addr + const.ZONE_SETPOINT_ADDR_OFFSET)
                temperature_raw = modbus.read_register(zone_addr + const.ZONE_TEMP_ADDR_OFFSET)
                humidity = modbus.read_register(zone_addr + const.ZONE_RH_ADDR_OFFSET)
                
                # Decode values
                setpoint = dpt_9001.unpack_dpt9001(setpoint_raw)
                temperature = dpt_9001.unpack_dpt9001(temperature_raw)
                
                zones.append({
                    'base_id': bid,
                    'zone_id': zid,
                    'state': state,
                    'setpoint': round(setpoint, 1),
                    'temperature': round(temperature, 1),
                    'relative_humidity': humidity,
                    'active': state > 0
                })
                
            except Exception as e:
                logger.warning(f"Failed to read zone {bid}/{zid}: {e}")
                # Continue with other zones
    
    return jsonify({
        'zones': zones,
        'count': len(zones),
        'filter': {
            'base_id': base_id,
            'include_inactive': include_inactive
        }
    }), 200


@zones_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found', 'status': 404}), 404


@zones_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.exception("Internal server error")
    return jsonify({'error': 'Internal server error', 'status': 500}), 500 