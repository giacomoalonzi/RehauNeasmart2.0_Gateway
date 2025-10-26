#!/usr/bin/env python3

import logging
import asyncio
from typing import Tuple
from models.zone_models import ZoneData, ZoneRequest
import const
import dpt_9001
from modbus_monitor import get_monitor
from modbus_client import get_client

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
        zone_addr = (base_id - 1) * const.ZONE_BASE_ID_MULTIPLIER + zone_id * const.ZONE_ID_MULTIPLIER
        
        # Log API read
        monitor = get_monitor()
        monitor.log_read(self.slave_id, zone_addr, count=1, source="api")
        
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
    
    def get_zone_labels(self, base_id: int, zone_id: int) -> Tuple[str, str]:
        """
        Get zone and base labels from configuration.
        
        Args:
            base_id (int): Base ID
            zone_id (int): Zone ID
            
        Returns:
            Tuple[str, str]: (base_label, zone_label)
        """
        from config import config_manager
        
        # Get zones configuration
        zones_config = config_manager.get_zones_config()
        structures = zones_config.get('structures', [])
        
        # Find the structure and zone
        for structure in structures:
            if structure.get('base_id') == base_id:
                base_label = structure.get('base_label', f'Base {base_id}')
                
                for zone in structure.get('zones', []):
                    if zone.get('id') == zone_id:
                        zone_label = zone.get('label', f'Zone {zone_id}')
                        return base_label, zone_label
                
                # If zone not found in structure, return default
                return base_label, f'Zone {zone_id}'
        
        # If structure not found, return defaults
        return f'Base {base_id}', f'Zone {zone_id}'

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
        zone_addr = (base_id - 1) * const.ZONE_BASE_ID_MULTIPLIER + zone_id * const.ZONE_ID_MULTIPLIER
        dpt_9001_setpoint = None
        
        if request.state is not None:
            if not isinstance(request.state, list):
                request.state = [request.state]
            
            # Log API write
            monitor = get_monitor()
            monitor.log_write(self.slave_id, zone_addr, request.state, source="api")
            
            self.context[self.slave_id].setValues(
                const.WRITE_HR_CODE,
                zone_addr,
                request.state
            )
        
        if request.setpoint is not None:
            dpt_9001_setpoint = dpt_9001.pack_dpt9001(request.setpoint)
            _logger.info(f"dpt_9001_setpoint: {dpt_9001_setpoint}")
            
            if not isinstance(dpt_9001_setpoint, list):
                dpt_9001_setpoint = [dpt_9001_setpoint]
            
            # Log API write
            monitor = get_monitor()
            monitor.log_write(self.slave_id, zone_addr + const.ZONE_SETPOINT_ADDR_OFFSET, 
                            dpt_9001_setpoint, source="api")
            
            # Write to local server registers
            self.context[self.slave_id].setValues(
                const.WRITE_HR_CODE,
                zone_addr + const.ZONE_SETPOINT_ADDR_OFFSET,
                dpt_9001_setpoint
            )
            
            # Write-through to physical Neasmart device
            write_through_success = False
            write_through_verified = False
            try:
                client = get_client(force_recreate=True)  # Force recreation to pick up new config
                success, msg = asyncio.run(
                    client.write_zone_setpoint(base_id, zone_id, dpt_9001_setpoint[0])
                )
                if success:
                    _logger.info(f"Write-through to physical device successful: {msg}")
                    write_through_success = True
                    # Check if this was a verified-after-timeout success
                    if "verified after timeout" in msg.lower():
                        write_through_verified = True
                        _logger.warning(f"Write succeeded but required verification due to timeout: {msg}")
                else:
                    _logger.warning(f"Write-through to physical device failed: {msg}")
                    # Log the specific error for debugging
                    _logger.warning(f"Write-through error details: {msg}")
            except Exception as e:
                _logger.error(f"Error during write-through to physical device: {e}")
                # Log the full exception for debugging
                import traceback
                _logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # If write-through failed, log appropriate warning
            if not write_through_success:
                _logger.warning("Write-through to physical device failed. Data saved locally but may not persist on device restart.")
                _logger.warning("Check Waveshare gateway connection and Neasmart device communication.")
            elif write_through_verified:
                _logger.info("Write-through succeeded with verification. Device communication may be slow but functional.")
        
        return True, "Zone updated successfully", dpt_9001_setpoint
