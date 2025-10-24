#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Union


@dataclass
class DeviceData:
    """Base device data model."""
    
    state: int
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {'state': self.state}


@dataclass
class DehumidifierData(DeviceData):
    """Dehumidifier data model for API responses."""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {'dehumidifierState': self.state}  # camelCase for frontend


@dataclass
class PumpData(DeviceData):
    """Pump data model for API responses."""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {'pumpState': self.state}  # camelCase for frontend


@dataclass
class MixedGroupData:
    """Mixed group data model for API responses."""
    
    pump_state: int
    mixing_valve_opening_percentage: int
    flow_temperature: float
    return_temperature: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'pumpState': self.pump_state,  # camelCase for frontend
            'mixingValveOpeningPercentage': self.mixing_valve_opening_percentage,  # camelCase for frontend
            'flowTemperature': self.flow_temperature,  # camelCase for frontend
            'returnTemperature': self.return_temperature  # camelCase for frontend
        }
