#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class ZoneData:
    """Zone data model for API responses."""
    
    state: int
    setpoint: float
    temperature: float
    relative_humidity: int
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'state': self.state,
            'setpoint': self.setpoint,
            'temperature': self.temperature,
            'relativeHumidity': self.relative_humidity  # camelCase for frontend
        }


@dataclass
class ZoneRequest:
    """Zone request model for API inputs."""
    
    state: Optional[int] = None
    setpoint: Optional[Union[int, float]] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ZoneRequest':
        """Create ZoneRequest from dictionary."""
        return cls(
            state=data.get('state'),
            setpoint=data.get('setpoint')
        )
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate zone request data.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if self.state is None and self.setpoint is None:
            return False, "one of state or setpoint need to be specified"
        
        if self.state is not None:
            if not isinstance(self.state, int) or self.state == 0 or self.state > 6:
                return False, "invalid state"
        
        if self.setpoint is not None:
            if not isinstance(self.setpoint, (int, float)):
                return False, "invalid setpoint"
        
        return True, ""
