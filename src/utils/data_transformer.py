#!/usr/bin/env python3

"""
Data transformation utilities for API responses.

This module provides utilities to transform data between backend (snake_case)
and frontend (camelCase) formats for API responses.
"""

import re
from typing import Any, Dict, List, Union


def to_camel_case(snake_str: str) -> str:
    """
    Convert snake_case string to camelCase.
    
    Args:
        snake_str (str): String in snake_case format
        
    Returns:
        str: String in camelCase format
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])


def to_snake_case(camel_str: str) -> str:
    """
    Convert camelCase string to snake_case.
    
    Args:
        camel_str (str): String in camelCase format
        
    Returns:
        str: String in snake_case format
    """
    # Insert an underscore before any uppercase letter that follows a lowercase letter
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def transform_dict_to_camel_case(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform dictionary keys from snake_case to camelCase.
    
    Args:
        data (Dict[str, Any]): Dictionary with snake_case keys
        
    Returns:
        Dict[str, Any]: Dictionary with camelCase keys
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        camel_key = to_camel_case(key)
        if isinstance(value, dict):
            result[camel_key] = transform_dict_to_camel_case(value)
        elif isinstance(value, list):
            result[camel_key] = [
                transform_dict_to_camel_case(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[camel_key] = value
    
    return result


def transform_dict_to_snake_case(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform dictionary keys from camelCase to snake_case.
    
    Args:
        data (Dict[str, Any]): Dictionary with camelCase keys
        
    Returns:
        Dict[str, Any]: Dictionary with snake_case keys
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        snake_key = to_snake_case(key)
        if isinstance(value, dict):
            result[snake_key] = transform_dict_to_snake_case(value)
        elif isinstance(value, list):
            result[snake_key] = [
                transform_dict_to_snake_case(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[snake_key] = value
    
    return result


def transform_api_response(data: Union[Dict, List, Any], to_camel: bool = True) -> Union[Dict, List, Any]:
    """
    Transform API response data between snake_case and camelCase.
    
    Args:
        data: Data to transform
        to_camel (bool): If True, convert to camelCase; if False, convert to snake_case
        
    Returns:
        Transformed data
    """
    if isinstance(data, dict):
        return transform_dict_to_camel_case(data) if to_camel else transform_dict_to_snake_case(data)
    elif isinstance(data, list):
        return [
            transform_api_response(item, to_camel) for item in data
        ]
    else:
        return data


# Common field mappings for API transformations
FIELD_MAPPINGS = {
    # Backend to Frontend (snake_case → camelCase)
    'operation_mode': 'operationMode',
    'operation_state': 'operationState', 
    'outside_temperature': 'outsideTemperature',
    'filtered_outside_temperature': 'filteredOutsideTemperature',
    'relative_humidity': 'relativeHumidity',
    'zone_id': 'zoneId',
    'base_id': 'baseId',
    'setpoint': 'setpoint',
    'temperature': 'temperature',
    'state': 'state',
    
    # Frontend to Backend (camelCase → snake_case)
    'operationMode': 'operation_mode',
    'operationState': 'operation_state',
    'outsideTemperature': 'outside_temperature', 
    'filteredOutsideTemperature': 'filtered_outside_temperature',
    'relativeHumidity': 'relative_humidity',
    'zoneId': 'zone_id',
    'baseId': 'base_id'
}


def apply_field_mappings(data: Dict[str, Any], reverse: bool = False) -> Dict[str, Any]:
    """
    Apply specific field mappings for API transformations.
    
    Args:
        data (Dict[str, Any]): Data to transform
        reverse (bool): If True, apply reverse mappings (camelCase → snake_case)
        
    Returns:
        Dict[str, Any]: Transformed data with mapped fields
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    mappings = {v: k for k, v in FIELD_MAPPINGS.items()} if reverse else FIELD_MAPPINGS
    
    for key, value in data.items():
        mapped_key = mappings.get(key, key)
        if isinstance(value, dict):
            result[mapped_key] = apply_field_mappings(value, reverse)
        elif isinstance(value, list):
            result[mapped_key] = [
                apply_field_mappings(item, reverse) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[mapped_key] = value
    
    return result
