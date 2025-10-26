#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Optional, Union

from utils import state_converter


@dataclass
class ZoneData:
    """Zone data model for API responses."""
    
    state: int
    setpoint: float
    temperature: float
    relative_humidity: int
    
    def to_dict(self, readable: bool = True) -> dict:
        """Convert to dictionary for JSON serialization."""
        state_value = state_converter.zone_state_to_name(self.state) if readable else self.state
        return {
            'state': state_value,
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
        """Create ZoneRequest from dictionary with string state."""
        state_value = data.get('state')
        if state_value is not None:
            # API should only accept strings, not integers
            if isinstance(state_value, int):
                raise ValueError("API only accepts string states, not integers")
            # Convert string state to integer for internal use
            state_value = state_converter.name_to_zone_state(state_value)
        return cls(
            state=state_value,
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
            # State should be an integer (converted from string in from_dict)
            # Zone states are limited to 0-4 (off, presence, away, standby, scheduled)
            if not isinstance(self.state, int) or self.state < 0 or self.state > 4:
                return False, "invalid state"
        
        if self.setpoint is not None:
            if not isinstance(self.setpoint, (int, float)):
                return False, "invalid setpoint"
        
        return True, ""
