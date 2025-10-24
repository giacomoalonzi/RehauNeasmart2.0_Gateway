#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Dict, Tuple, Union

from utils import state_converter


@dataclass
class OperationMode:
    """Operation mode data model."""
    
    mode: int
    
    def to_dict(self, readable: bool = False) -> dict:
        """Convert to dictionary for JSON serialization."""
        value: Union[int, str] = state_converter.mode_to_name(self.mode) if readable else self.mode
        return {'mode': value}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Union[int, str]]) -> 'OperationMode':
        """Create OperationMode from dictionary allowing string or int."""
        value = data.get('mode')
        normalized = state_converter.name_to_mode(value)
        return cls(mode=normalized)
    
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
    
    def to_dict(self, readable: bool = False) -> dict:
        """Convert to dictionary for JSON serialization."""
        value: Union[int, str] = state_converter.state_to_name(self.state) if readable else self.state
        return {'state': value}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Union[int, str]]) -> 'OperationState':
        """Create OperationState from dictionary allowing string or int."""
        value = data.get('state')
        normalized = state_converter.name_to_state(value)
        return cls(state=normalized)
    
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
