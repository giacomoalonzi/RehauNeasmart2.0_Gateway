#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ApiResponse:
    """Generic API response model."""
    
    data: Any
    status: int = 200
    message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        response = {'data': self.data}
        if self.message:
            response['message'] = self.message
        return response


@dataclass
class ErrorResponse:
    """Error response model."""
    
    error: str
    status: int = 400
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {'err': self.error}


@dataclass
class TemperatureData:
    """Temperature data model for API responses."""
    
    outside_temperature: Optional[float]
    filtered_outside_temperature: Optional[float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'outsideTemperature': self.outside_temperature,  # camelCase for frontend
            'filteredOutsideTemperature': self.filtered_outside_temperature  # camelCase for frontend
        }


@dataclass
class NotificationData:
    """Notification data model for API responses."""
    
    hints_present: bool
    warnings_present: bool
    error_present: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'hintsPresent': self.hints_present,  # camelCase for frontend
            'warningsPresent': self.warnings_present,  # camelCase for frontend
            'errorPresent': self.error_present  # camelCase for frontend
        }
