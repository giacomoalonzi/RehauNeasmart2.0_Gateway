#!/usr/bin/env python3

import logging
from typing import Tuple
from models.device_models import DehumidifierData, PumpData, MixedGroupData
import const
import dpt_9001

_logger = logging.getLogger(__name__)


class DeviceService:
    """Service for device-related business logic."""
    
    def __init__(self, context, slave_id: int):
        """
        Initialize device service.
        
        Args:
            context: Modbus context
            slave_id (int): Modbus slave ID
        """
        self.context = context
        self.slave_id = slave_id
    
    def validate_dehumidifier_id(self, dehumidifier_id: int) -> Tuple[bool, str]:
        """
        Validate dehumidifier ID.
        
        Args:
            dehumidifier_id (int): Dehumidifier ID (1-9)
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if dehumidifier_id > 9 or dehumidifier_id < 1:
            return False, "invalid dehumidifier id"
        return True, ""
    
    def validate_pump_id(self, pump_id: int) -> Tuple[bool, str]:
        """
        Validate pump ID.
        
        Args:
            pump_id (int): Pump ID (1-5)
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if pump_id > 5 or pump_id < 1:
            return False, "invalid pump id"
        return True, ""
    
    def validate_mixed_group_id(self, group_id: int) -> Tuple[bool, str]:
        """
        Validate mixed group ID.
        
        Args:
            group_id (int): Group ID (1-3)
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if group_id == 0 or group_id > 3:
            return False, "invalid mixed group id"
        return True, ""
    
    def get_dehumidifier_data(self, dehumidifier_id: int) -> DehumidifierData:
        """
        Get dehumidifier data from Modbus registers.
        
        Args:
            dehumidifier_id (int): Dehumidifier ID
            
        Returns:
            DehumidifierData: Dehumidifier data object
        """
        state = self.context[self.slave_id].getValues(
            const.READ_HR_CODE,
            dehumidifier_id + const.DEHUMIDIFIERS_ADDR_OFFSET,
            count=1
        )[0]
        
        return DehumidifierData(state=state)
    
    def get_pump_data(self, pump_id: int) -> PumpData:
        """
        Get pump data from Modbus registers.
        
        Args:
            pump_id (int): Pump ID
            
        Returns:
            PumpData: Pump data object
        """
        state = self.context[self.slave_id].getValues(
            const.READ_HR_CODE,
            pump_id + const.EXTRA_PUMPS_ADDR_OFFSET,
            count=1
        )[0]
        
        return PumpData(state=state)
    
    def get_mixed_group_data(self, group_id: int) -> MixedGroupData:
        """
        Get mixed group data from Modbus registers.
        
        Args:
            group_id (int): Group ID
            
        Returns:
            MixedGroupData: Mixed group data object
        """
        base_reg = const.MIXEDGROUP_BASE_REG[group_id]
        
        pump_state = self.context[self.slave_id].getValues(
            const.READ_HR_CODE,
            base_reg + const.MIXEDGROUP_PUMP_STATE_OFFSET,
            count=1
        )[0]
        
        mixing_valve_opening_percentage = self.context[self.slave_id].getValues(
            const.READ_HR_CODE,
            base_reg + const.MIXEDGROUP_VALVE_OPENING_OFFSET,
            count=1
        )[0]
        
        flow_temperature = dpt_9001.unpack_dpt9001(
            self.context[self.slave_id].getValues(
                const.READ_HR_CODE,
                base_reg + const.MIXEDGROUP_FLOW_TEMP_OFFSET,
                count=1
            )[0]
        )
        
        return_temperature = dpt_9001.unpack_dpt9001(
            self.context[self.slave_id].getValues(
                const.READ_HR_CODE,
                base_reg + const.MIXEDGROUP_RETURN_TEMP_OFFSET,
                count=1
            )[0]
        )
        
        return MixedGroupData(
            pump_state=pump_state,
            mixing_valve_opening_percentage=mixing_valve_opening_percentage,
            flow_temperature=flow_temperature,
            return_temperature=return_temperature
        )
