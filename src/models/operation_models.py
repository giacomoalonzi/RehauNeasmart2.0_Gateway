#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Dict, Tuple, Union

from utils import state_converter


@dataclass
class OperationMode:
    """Operation mode data model."""
    
    mode: int
    
    def to_dict(self, readable: bool = True) -> dict:
        """Convert to dictionary for JSON serialization."""
        value: Union[int, str] = state_converter.mode_to_name(self.mode) if readable else self.mode
        return {'mode': value}
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'OperationMode':
        """Create OperationMode from dictionary with string mode."""
        value = data.get('mode')
        # API should only accept strings, not integers
        if isinstance(value, int):
            raise ValueError("API only accepts string modes, not integers")
        normalized = state_converter.name_to_mode(value)
        return cls(mode=normalized)
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate operation mode data.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if self.mode is None:
            return False, "missing mode key in payload"
        
        # Mode should be an integer (converted from string in from_dict)
        # Valid range is 1-5 according to system specification
        if not isinstance(self.mode, int) or self.mode < 1 or self.mode > 5:
            return False, "invalid mode"
        
        return True, ""


@dataclass
class OperationState:
    """Operation state data model."""
    
    state: int
    
    def to_dict(self, readable: bool = True) -> dict:
        """Convert to dictionary for JSON serialization."""
        value: Union[int, str] = state_converter.state_to_name(self.state) if readable else self.state
        return {'state': value}
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'OperationState':
        """Create OperationState from dictionary with string state."""
        value = data.get('state')
        # API should only accept strings, not integers
        if isinstance(value, int):
            raise ValueError("API only accepts string states, not integers")
        normalized = state_converter.name_to_state(value)
        return cls(state=normalized)
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate operation state data.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # State should be an integer (converted from string in from_dict)
        # Valid range is 0-6 (0 = off, 1-6 = various operation states)
        if not isinstance(self.state, int) or self.state < 0 or self.state > 6:
            return False, "invalid state"
        
        return True, ""
