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
from config import get_config, APIConfig, AppConfig

logger = logging.getLogger(__name__)

zones_bp = Blueprint('zones', __name__, url_prefix='/api/v1/zones')


class APIError(Exception):
    """Base API error"""
    status_code = 500
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict] = None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.details = details
    
    def to_dict(self) -> Dict[str, Any]:
        data = {'error': self.message, 'status': self.status_code}
        if self.details:
            data['details'] = self.details
        return data


class ValidationError(APIError):
    """Validation error"""
    status_code = 400


class NotFoundError(APIError):
    """Resource not found error"""
    status_code = 404


def get_zone_labels(base_id: int, zone_id: int, config: AppConfig) -> (str, str):
    """Get labels for base and zone from configuration"""
    zones_conf = getattr(config, 'zones', {}) or {}
    base_conf = zones_conf.get(str(base_id), {})
    base_label = base_conf.get('label', f"Base {base_id}")
    zone_label = base_conf.get('zones', {}).get(str(zone_id), f"Zone {zone_id}")
    return base_label, zone_label


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


def validate_and_convert_state(state: str) -> int:
    """Validate and convert descriptive state to numeric"""
    if not isinstance(state, str):
        raise ValidationError("State must be a string (e.g., 'presence', 'off')")
    
    numeric_state = const.STATE_MAPPING_REVERSE.get(state.lower())
    if numeric_state is None:
        valid_states = list(const.STATE_MAPPING_REVERSE.keys())
        raise ValidationError(f"Invalid state: {state}. Must be one of {valid_states}")
    
    return numeric_state


def validate_setpoint(setpoint: float) -> None:
    """Validate temperature setpoint"""
    if not 5.0 <= setpoint <= 40.0:
        raise ValidationError(f"Invalid setpoint: {setpoint}. Must be between 5.0 and 40.0°C")


def calculate_zone_address(base_id: int, zone_id: int) -> int:
    """Calculate zone address from base and zone IDs"""
    return (base_id - 1) * const.NEASMART_BASE_SLAVE_ADDR + zone_id * const.BASE_ZONE_ID


def format_temperature(value: float, config: APIConfig) -> Dict[str, Any]:
    """Format temperature with units"""
    return {'value': round(value, 1), 'unit': config.temperature_unit}


@zones_bp.route('/<int:base_id>/<int:zone_id>', methods=['GET'])
@handle_errors
def get_zone(base_id: int, zone_id: int):
    """Get structured zone information"""
    validate_base_id(base_id)
    validate_zone_id(zone_id)
    
    config = get_config()
    modbus = get_modbus_manager()
    zone_addr = calculate_zone_address(base_id, zone_id)
    base_label, zone_label = get_zone_labels(base_id, zone_id, config)

    try:
        # Read state first
        state_numeric = modbus.read_register(zone_addr)
        state_str = const.STATE_MAPPING.get(state_numeric, "unknown")
        
        # Determine if we should update the setpoint in the database
        update_db_for_setpoint = state_str != "off"
        
        setpoint_raw = modbus.read_register(
            zone_addr + const.ZONE_SETPOINT_ADDR_OFFSET,
            update_db=update_db_for_setpoint
        )
        temperature_raw = modbus.read_register(zone_addr + const.ZONE_TEMP_ADDR_OFFSET)
        humidity = modbus.read_register(zone_addr + const.ZONE_RH_ADDR_OFFSET)
        
        temperature = dpt_9001.unpack_dpt9001(temperature_raw)
        
        # Handle setpoint
        if state_str == "off":
            setpoint_obj = None # No setpoint when off
        else:
            setpoint = dpt_9001.unpack_dpt9001(setpoint_raw)
            setpoint_obj = format_temperature(setpoint, config.api)
        
    except Exception as e:
        logger.error(f"Failed to read zone {base_id}/{zone_id}: {e}")
        raise ModbusException(f"Failed to read zone data: {str(e)}")
    
    # Prepare response
    response_data = {
        'base': {
            'id': base_id,
            'label': base_label
        },
        'zone': {
            'id': zone_id,
            'label': zone_label
        },
        'state': state_str,
        'temperature': format_temperature(temperature, config.api),
        'setpoint': setpoint_obj,
        'relative_humidity': humidity,
        'address': zone_addr
    }
    
    return jsonify(response_data), 200


@zones_bp.route('/<int:base_id>/<int:zone_id>', methods=['POST'])
@handle_errors
def update_zone(base_id: int, zone_id: int):
    """Update zone parameters with descriptive state"""
    validate_base_id(base_id)
    validate_zone_id(zone_id)
    
    if not request.is_json:
        raise ValidationError("Request must be JSON")
    
    data = request.get_json()
    state_str = data.get('state')
    setpoint = data.get('setpoint')
    
    if state_str is None and setpoint is None:
        raise ValidationError("At least one of 'state' or 'setpoint' must be provided")
    
    zone_addr = calculate_zone_address(base_id, zone_id)
    modbus = get_modbus_manager()
    
    response_data = {
        'base': {'id': base_id},
        'zone': {'id': zone_id},
        'updated': {}
    }
    
    # Update state if provided
    if state_str is not None:
        state_numeric = validate_and_convert_state(state_str)
        try:
            modbus.write_register(zone_addr, state_numeric)
            response_data['updated']['state'] = state_str
        except Exception as e:
            raise ModbusException(f"Failed to update state: {str(e)}")
    
    # Update setpoint, but only if state is not being set to 'off' in the same request
    if setpoint is not None:
        if state_str is not None and state_str.lower() == 'off':
            logger.warning("Ignoring setpoint update because state is being set to 'off'")
        else:
            if not isinstance(setpoint, (int, float)):
                raise ValidationError("Setpoint must be a number")
            
            validate_setpoint(float(setpoint))
            
            try:
                encoded_setpoint = dpt_9001.pack_dpt9001(float(setpoint))
                modbus.write_register(zone_addr + const.ZONE_SETPOINT_ADDR_OFFSET, encoded_setpoint)
                response_data['updated']['setpoint'] = float(setpoint)
            except Exception as e:
                raise ModbusException(f"Failed to update setpoint: {str(e)}")
    
    return jsonify(response_data), 200


@zones_bp.route('/', methods=['GET'])
@handle_errors
def list_zones():
    """List all configured zones with their structured status"""
    config = get_config()
    zones_conf = getattr(config, 'zones', {}) or {}
    
    if not zones_conf:
        return jsonify({
            'zones': [], 'count': 0, 'message': 'No zones configured. Please add zones to your config file.'
        }), 200
        
    modbus = get_modbus_manager()
    zones = []
    
    for base_id_str, base_config in zones_conf.items():
        base_id = int(base_id_str)
        for zone_id_str, zone_label in base_config.get('zones', {}).items():
            zone_id = int(zone_id_str)
            try:
                zone_addr = calculate_zone_address(base_id, zone_id)
                state_numeric = modbus.read_register(zone_addr)
                state_str = const.STATE_MAPPING.get(state_numeric, "unknown")
                
                # Skip inactive zones by default
                if state_numeric == 0:
                    continue
                
                temperature_raw = modbus.read_register(zone_addr + const.ZONE_TEMP_ADDR_OFFSET)
                humidity = modbus.read_register(zone_addr + const.ZONE_RH_ADDR_OFFSET)
                temperature = dpt_9001.unpack_dpt9001(temperature_raw)
                
                setpoint_obj = None
                if state_str != 'off':
                    setpoint_raw = modbus.read_register(
                        zone_addr + const.ZONE_SETPOINT_ADDR_OFFSET,
                        update_db=False # Don't pollute DB on list view
                    )
                    setpoint = dpt_9001.unpack_dpt9001(setpoint_raw)
                    setpoint_obj = format_temperature(setpoint, config.api)

                zones.append({
                    'base': {'id': base_id, 'label': base_config.get('label')},
                    'zone': {'id': zone_id, 'label': zone_label},
                    'state': state_str,
                    'temperature': format_temperature(temperature, config.api),
                    'setpoint': setpoint_obj
                })
            except Exception as e:
                logger.warning(f"Failed to read zone {base_id}/{zone_id} during list operation: {e}")

    return jsonify({'zones': zones, 'count': len(zones)}), 200


@zones_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found', 'status': 404}), 404


@zones_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.exception("Internal server error")
    return jsonify({'error': 'Internal server error', 'status': 500}), 500 