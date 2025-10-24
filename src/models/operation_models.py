#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Union


@dataclass
class OperationMode:
    """Operation mode data model."""
    
    mode: int
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {'mode': self.mode}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OperationMode':
        """Create OperationMode from dictionary."""
        return cls(mode=data.get('mode'))
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate operation mode data.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not self.mode:
            return False, "missing mode key in payload"
        
        if not isinstance(self.mode, int) or self.mode == 0 or self.mode > 5:
            return False, "invalid mode"
        
        return True, ""


@dataclass
class OperationState:
    """Operation state data model."""
    
    state: int
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {'state': self.state}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OperationState':
        """Create OperationState from dictionary."""
        return cls(state=data.get('state'))
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate operation state data.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not self.state:
            return False, "missing state key in payload"
        
        if not isinstance(self.state, int) or self.state == 0 or self.state > 6:
            return False, "invalid state"
        
        return True, ""
