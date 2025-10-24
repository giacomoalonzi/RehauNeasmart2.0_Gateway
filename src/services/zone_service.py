#!/usr/bin/env python3

import logging
from typing import Tuple
from models.zone_models import ZoneData, ZoneRequest
import const
import dpt_9001

_logger = logging.getLogger(__name__)


class ZoneService:
    """Service for zone-related business logic."""
    
    def __init__(self, context, slave_id: int):
        """
        Initialize zone service.
        
        Args:
            context: Modbus context
            slave_id (int): Modbus slave ID
        """
        self.context = context
        self.slave_id = slave_id
    
    def validate_zone_params(self, base_id: int, zone_id: int) -> Tuple[bool, str]:
        """
        Validate zone parameters.
        
        Args:
            base_id (int): Base ID (1-4)
            zone_id (int): Zone ID (1-12)
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if base_id > 4 or base_id < 1:
            return False, "invalid base id"
        
        if zone_id > 12 or zone_id < 1:
            return False, "invalid zone id"
        
        return True, ""
    
    def get_zone_data(self, base_id: int, zone_id: int) -> ZoneData:
        """
        Get zone data from Modbus registers.
        
        Args:
            base_id (int): Base ID
            zone_id (int): Zone ID
            
        Returns:
            ZoneData: Zone data object
        """
        zone_addr = (base_id - 1) * const.NEASMART_BASE_SLAVE_ADDR + zone_id * const.BASE_ZONE_ID
        
        state = self.context[self.slave_id].getValues(
            const.READ_HR_CODE,
            zone_addr,
            count=1
        )[0]
        
        setpoint = dpt_9001.unpack_dpt9001(
            self.context[self.slave_id].getValues(
                const.READ_HR_CODE,
                zone_addr + const.ZONE_SETPOINT_ADDR_OFFSET,
                count=1
            )[0]
        )
        
        temperature = dpt_9001.unpack_dpt9001(
            self.context[self.slave_id].getValues(
                const.READ_HR_CODE,
                zone_addr + const.ZONE_TEMP_ADDR_OFFSET,
                count=1
            )[0]
        )
        
        relative_humidity = self.context[self.slave_id].getValues(
            const.READ_HR_CODE,
            zone_addr + const.ZONE_RH_ADDR_OFFSET,
            count=1
        )[0]
        
        return ZoneData(
            state=state,
            setpoint=setpoint,
            temperature=temperature,
            relative_humidity=relative_humidity
        )
    
    def update_zone_data(self, base_id: int, zone_id: int, request: ZoneRequest) -> Tuple[bool, str, any]:
        """
        Update zone data in Modbus registers.
        
        Args:
            base_id (int): Base ID
            zone_id (int): Zone ID
            request (ZoneRequest): Update request
            
        Returns:
            Tuple[bool, str, any]: (success, message, dpt_9001_setpoint)
        """
        zone_addr = (base_id - 1) * const.NEASMART_BASE_SLAVE_ADDR + zone_id * const.BASE_ZONE_ID
        dpt_9001_setpoint = None
        
        if request.state is not None:
            if not isinstance(request.state, list):
                request.state = [request.state]
            self.context[self.slave_id].setValues(
                const.READ_HR_CODE,
                zone_addr,
                request.state
            )
        
        if request.setpoint is not None:
            dpt_9001_setpoint = dpt_9001.pack_dpt9001(request.setpoint)
            _logger.info(f"dpt_9001_setpoint: {dpt_9001_setpoint}")
            
            if not isinstance(dpt_9001_setpoint, list):
                dpt_9001_setpoint = [dpt_9001_setpoint]
            
            self.context[self.slave_id].setValues(
                const.READ_HR_CODE,
                zone_addr + const.ZONE_SETPOINT_ADDR_OFFSET,
                dpt_9001_setpoint
            )
        
        return True, "Zone updated successfully", dpt_9001_setpoint
