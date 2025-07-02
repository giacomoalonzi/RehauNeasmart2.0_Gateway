#!/usr/bin/env python3
"""
Shared error classes and handlers for the API.
"""

import logging
from typing import Dict, Any, Optional
from flask import jsonify
from functools import wraps

from modbus_manager import ModbusException

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base class for custom API errors."""
    status_code = 500
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict] = None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.details = details
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary."""
        data = {'error': self.message, 'status': self.status_code}
        if self.details:
            data['details'] = self.details
        return data


class ValidationError(APIError):
    """Raised when request data is invalid."""
    status_code = 400


class NotFoundError(APIError):
    """Raised when a resource is not found."""
    status_code = 404


def handle_errors(f):
    """
    A decorator to catch and handle exceptions for API endpoints.
    It standardizes error responses for APIError, ModbusException, and other exceptions.
    """
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