#!/usr/bin/env python3

import logging
from models.response_models import TemperatureData
import const
import dpt_9001

_logger = logging.getLogger(__name__)


class TemperatureService:
    """Service for temperature-related business logic."""
    
    def __init__(self, context, slave_id: int):
        """
        Initialize temperature service.
        
        Args:
            context: Modbus context
            slave_id (int): Modbus slave ID
        """
        self.context = context
        self.slave_id = slave_id
    
    def get_outside_temperature_data(self) -> TemperatureData:
        """
        Get outside temperature data from Modbus registers.
        
        Returns:
            TemperatureData: Temperature data object
        """
        outside_temperature = dpt_9001.unpack_dpt9001(
            self.context[self.slave_id].getValues(
                const.READ_HR_CODE,
                const.OUTSIDE_TEMP_REG,
                count=1
            )[0]
        )
        
        filtered_outside_temperature = dpt_9001.unpack_dpt9001(
            self.context[self.slave_id].getValues(
                const.READ_HR_CODE,
                const.FILTERED_OUTSIDE_TEMP_REG,
                count=1
            )[0]
        )
        
        return TemperatureData(
            outside_temperature=outside_temperature,
            filtered_outside_temperature=filtered_outside_temperature
        )
