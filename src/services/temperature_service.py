#!/usr/bin/env python3

import logging
from models.response_models import TemperatureData
import const
import dpt_9001

_logger = logging.getLogger(__name__)


class TemperatureService:
    """Service for temperature-related business logic."""
    
    # Reasonable temperature range for outside temperature validation
    MIN_REASONABLE_TEMP = -50.0  # -50°C (extreme cold)
    MAX_REASONABLE_TEMP = 60.0   # 60°C (extreme heat)
    
    def __init__(self, context, slave_id: int):
        """
        Initialize temperature service.
        
        Args:
            context: Modbus context
            slave_id (int): Modbus slave ID
        """
        self.context = context
        self.slave_id = slave_id
    
    def _validate_temperature(self, temperature: float, sensor_name: str) -> float:
        """
        Validate temperature reading and handle invalid values.
        
        Args:
            temperature (float): Temperature value to validate
            sensor_name (str): Name of the sensor for logging
            
        Returns:
            float: Validated temperature or None if invalid
        """
        # Check for obviously invalid values
        if temperature is None:
            _logger.warning(f"{sensor_name}: Temperature reading is None")
            return None
            
        # Check for extreme values that indicate sensor issues
        if temperature < self.MIN_REASONABLE_TEMP or temperature > self.MAX_REASONABLE_TEMP:
            _logger.error(
                f"{sensor_name}: Temperature {temperature}°C is outside reasonable range "
                f"[{self.MIN_REASONABLE_TEMP}, {self.MAX_REASONABLE_TEMP}]. "
                f"This may indicate a sensor malfunction or uninitialized data."
            )
            return None
            
        # Check for DPT 9001 maximum values that indicate uninitialized data
        if abs(temperature - dpt_9001.DPT9001_MAX_VALUE) < 0.01:
            _logger.error(
                f"{sensor_name}: Temperature {temperature}°C is at DPT 9001 maximum value. "
                f"This indicates uninitialized sensor data or sensor malfunction."
            )
            return None
            
        if abs(temperature - dpt_9001.DPT9001_MIN_VALUE) < 0.01:
            _logger.error(
                f"{sensor_name}: Temperature {temperature}°C is at DPT 9001 minimum value. "
                f"This indicates uninitialized sensor data or sensor malfunction."
            )
            return None
            
        return temperature
    
    def _read_temperature_register(self, address: int, sensor_name: str) -> float:
        """
        Read and validate a temperature register.
        
        Args:
            address (int): Register address
            sensor_name (str): Name of the sensor for logging
            
        Returns:
            float: Validated temperature or None if invalid
        """
        try:
            raw_value = self.context[self.slave_id].getValues(
                const.READ_HR_CODE,
                address,
                count=1
            )[0]
            
            _logger.debug(f"{sensor_name}: Raw register value: {raw_value} (0x{raw_value:04X})")
            
            # Check for uninitialized register (0x7FFF = 32767 = DPT 9001 max)
            if raw_value == 0x7FFF:
                _logger.error(
                    f"{sensor_name}: Register contains 0x7FFF (32767), indicating uninitialized data. "
                    f"This will decode to {dpt_9001.DPT9001_MAX_VALUE}°C which is invalid."
                )
                return None
                
            # Check for zero register (uninitialized)
            if raw_value == 0:
                _logger.warning(f"{sensor_name}: Register contains 0, indicating uninitialized data")
                return None
            
            # Decode the DPT 9001 value
            temperature = dpt_9001.unpack_dpt9001(raw_value)
            _logger.debug(f"{sensor_name}: Decoded temperature: {temperature}°C")
            
            # Validate the decoded temperature
            return self._validate_temperature(temperature, sensor_name)
            
        except Exception as e:
            _logger.error(f"{sensor_name}: Error reading temperature register {address}: {e}")
            return None
    
    def get_outside_temperature_data(self) -> TemperatureData:
        """
        Get outside temperature data from Modbus registers with validation.
        
        Returns:
            TemperatureData: Temperature data object with validated values
        """
        _logger.info("Reading outside temperature data from Modbus registers")
        
        # Read and validate outside temperature
        outside_temperature = self._read_temperature_register(
            const.OUTSIDE_TEMPERATURE_ADDR, 
            "Outside Temperature"
        )
        
        # Read and validate filtered outside temperature
        filtered_outside_temperature = self._read_temperature_register(
            const.FILTERED_OUTSIDE_TEMPERATURE_ADDR, 
            "Filtered Outside Temperature"
        )
        
        # Log the results
        if outside_temperature is not None:
            _logger.info(f"Outside temperature: {outside_temperature}°C")
        else:
            _logger.warning("Outside temperature reading is invalid or unavailable")
            
        if filtered_outside_temperature is not None:
            _logger.info(f"Filtered outside temperature: {filtered_outside_temperature}°C")
        else:
            _logger.warning("Filtered outside temperature reading is invalid or unavailable")
        
        return TemperatureData(
            outside_temperature=outside_temperature,
            filtered_outside_temperature=filtered_outside_temperature
        )
