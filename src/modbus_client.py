#!/usr/bin/env python3

"""
Modbus Client for Writing to Physical Neasmart Device

This module implements a Modbus TCP client that can write setpoints
directly to the physical Neasmart device through the Waveshare Gateway.
"""

import logging
import asyncio
import json
import os
from typing import Optional, Tuple
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException
import const

_logger = logging.getLogger(__name__)


class NeasmartModbusClient:
    """
    Modbus TCP client for communicating with the physical Neasmart device.
    
    This client connects to the Waveshare RS485-to-TCP gateway and writes
    setpoints directly to the Neasmart device to ensure changes persist.
    """
    
    def __init__(self, gateway_host: str = "192.168.1.200", gateway_port: int = 502, 
                 neasmart_slave_id: int = 240):
        """
        Initialize Modbus client.
        
        Args:
            gateway_host: IP address of Waveshare gateway
            gateway_port: Port of Waveshare gateway (usually 502)
            neasmart_slave_id: Modbus slave ID of the Neasmart device
        """
        self.gateway_host = gateway_host
        self.gateway_port = gateway_port
        self.neasmart_slave_id = neasmart_slave_id
        self.client: Optional[AsyncModbusTcpClient] = None
        self.connected = False
        self._connect_lock = asyncio.Lock()
        
        # Load gateway configuration
        self.config = self._load_gateway_config()
        self.consecutive_errors = 0
        self.last_error_time = 0
    
    def _load_gateway_config(self) -> dict:
        """Load gateway configuration from config file."""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'gateway.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            _logger.warning(f"Could not load gateway config: {e}. Using defaults.")
            return {
                "gateway": {"enabled": True},
                "fallback": {"disable_write_through_on_error": False, "max_consecutive_errors": 3}
            }
    
    def is_gateway_enabled(self) -> bool:
        """Check if gateway write-through is enabled."""
        if not self.config.get("gateway", {}).get("enabled", True):
            return False
        
        # Check if we should disable due to consecutive errors
        if self.config.get("fallback", {}).get("disable_write_through_on_error", False):
            max_errors = self.config.get("fallback", {}).get("max_consecutive_errors", 3)
            if self.consecutive_errors >= max_errors:
                _logger.warning(f"Gateway disabled due to {self.consecutive_errors} consecutive errors")
                return False
        
        return True
    
    def _record_error(self):
        """Record an error for fallback logic."""
        self.consecutive_errors += 1
        self.last_error_time = asyncio.get_event_loop().time()
        _logger.warning(f"Gateway error recorded. Consecutive errors: {self.consecutive_errors}")
    
    def _record_success(self):
        """Record a successful operation."""
        if self.consecutive_errors > 0:
            _logger.info(f"Gateway operation successful. Resetting error count from {self.consecutive_errors}")
            self.consecutive_errors = 0
    
    async def connect(self) -> bool:
        """
        Connect to the Waveshare gateway.
        
        Returns:
            bool: True if connected successfully
        """
        async with self._connect_lock:
            if self.connected and self.client:
                return True
            
            try:
                _logger.info(f"Connecting to Waveshare gateway at {self.gateway_host}:{self.gateway_port}")
                self.client = AsyncModbusTcpClient(
                    host=self.gateway_host,
                    port=self.gateway_port,
                    timeout=5
                )
                await self.client.connect()
                
                if self.client.connected:
                    self.connected = True
                    _logger.info("Successfully connected to Waveshare gateway")
                    return True
                else:
                    _logger.error("Failed to connect to Waveshare gateway")
                    return False
                    
            except Exception as e:
                _logger.error(f"Error connecting to Waveshare gateway: {e}")
                self.connected = False
                return False
    
    async def disconnect(self):
        """Disconnect from the Waveshare gateway."""
        if self.client:
            try:
                self.client.close()
                _logger.info("Disconnected from Waveshare gateway")
            except Exception as e:
                _logger.error(f"Error disconnecting: {e}")
            finally:
                self.connected = False
                self.client = None
    
    async def write_zone_setpoint(self, base_id: int, zone_id: int, 
                                  dpt_9001_value: int, max_retries: int = 3) -> Tuple[bool, str]:
        """
        Write setpoint to a zone on the physical Neasmart device.
        
        Args:
            base_id: Base ID (1-4)
            zone_id: Zone ID (1-12)
            dpt_9001_value: DPT 9001 encoded setpoint value
            max_retries: Maximum number of retry attempts
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Check if gateway is enabled
        if not self.is_gateway_enabled():
            return False, "Gateway write-through is disabled due to configuration or consecutive errors"
        
        # Calculate register address
        zone_addr = (base_id - 1) * const.ZONE_BASE_ID_MULTIPLIER + zone_id * const.ZONE_ID_MULTIPLIER
        setpoint_addr = zone_addr + const.ZONE_SETPOINT_ADDR_OFFSET
        
        _logger.info(f"Writing setpoint to Neasmart device: addr={setpoint_addr}, value={dpt_9001_value}")
        
        # Ensure connected
        if not self.connected:
            success = await self.connect()
            if not success:
                self._record_error()
                return False, "Failed to connect to Waveshare gateway"
        
        last_error = None
        for attempt in range(max_retries):
            try:
                _logger.info(f"Write attempt {attempt + 1}/{max_retries}")
                
                # Write single holding register (Modbus function code 6)
                response = await self.client.write_register(
                    address=setpoint_addr,
                    value=dpt_9001_value,
                    slave=self.neasmart_slave_id
                )
                
                if response.isError():
                    error_msg = f"Modbus write error: {response}"
                    _logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")
                    last_error = error_msg
                    
                    # If this is not the last attempt, wait before retrying
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)  # Wait 1 second before retry
                        continue
                    else:
                        self._record_error()
                        return False, error_msg
                
                _logger.info(f"Successfully wrote setpoint to Neasmart device on attempt {attempt + 1}")
                self._record_success()
                return True, "Setpoint written to physical device"
                
            except ModbusException as e:
                error_msg = f"Modbus exception on attempt {attempt + 1}: {e}"
                _logger.warning(error_msg)
                last_error = error_msg
                
                # If this is not the last attempt, wait before retrying
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # Wait 1 second before retry
                    continue
                else:
                    self._record_error()
                    return False, error_msg
                    
            except Exception as e:
                error_msg = f"Unexpected error on attempt {attempt + 1}: {e}"
                _logger.error(error_msg)
                last_error = error_msg
                
                # If this is not the last attempt, wait before retrying
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # Wait 1 second before retry
                    continue
                else:
                    self._record_error()
                    return False, error_msg
        
        # If we get here, all retries failed
        self._record_error()
        return False, f"All {max_retries} attempts failed. Last error: {last_error}"
    
    async def write_zone_state(self, base_id: int, zone_id: int, state: int) -> Tuple[bool, str]:
        """
        Write state to a zone on the physical Neasmart device.
        
        Args:
            base_id: Base ID (1-4)
            zone_id: Zone ID (1-12)
            state: Zone state value
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Calculate register address
        zone_addr = (base_id - 1) * const.ZONE_BASE_ID_MULTIPLIER + zone_id * const.ZONE_ID_MULTIPLIER
        
        _logger.info(f"Writing state to Neasmart device: addr={zone_addr}, value={state}")
        
        # Ensure connected
        if not self.connected:
            success = await self.connect()
            if not success:
                return False, "Failed to connect to Waveshare gateway"
        
        try:
            # Write single holding register (Modbus function code 6)
            response = await self.client.write_register(
                address=zone_addr,
                value=state,
                slave=self.neasmart_slave_id
            )
            
            if response.isError():
                error_msg = f"Modbus write error: {response}"
                _logger.error(error_msg)
                return False, error_msg
            
            _logger.info(f"Successfully wrote state to Neasmart device")
            return True, "State written to physical device"
            
        except ModbusException as e:
            error_msg = f"Modbus exception: {e}"
            _logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error writing state: {e}"
            _logger.error(error_msg)
            return False, error_msg
    
    async def read_zone_setpoint(self, base_id: int, zone_id: int) -> Tuple[bool, Optional[int], str]:
        """
        Read setpoint from the physical Neasmart device.
        
        Args:
            base_id: Base ID (1-4)
            zone_id: Zone ID (1-12)
            
        Returns:
            Tuple[bool, Optional[int], str]: (success, dpt_9001_value, message)
        """
        # Calculate register address
        zone_addr = (base_id - 1) * const.ZONE_BASE_ID_MULTIPLIER + zone_id * const.ZONE_ID_MULTIPLIER
        setpoint_addr = zone_addr + const.ZONE_SETPOINT_ADDR_OFFSET
        
        # Ensure connected
        if not self.connected:
            success = await self.connect()
            if not success:
                return False, None, "Failed to connect to Waveshare gateway"
        
        try:
            # Read holding register (Modbus function code 3)
            response = await self.client.read_holding_registers(
                address=setpoint_addr,
                count=1,
                slave=self.neasmart_slave_id
            )
            
            if response.isError():
                error_msg = f"Modbus read error: {response}"
                _logger.error(error_msg)
                return False, None, error_msg
            
            value = response.registers[0]
            _logger.info(f"Read setpoint from Neasmart device: addr={setpoint_addr}, value={value}")
            return True, value, "Successfully read setpoint"
            
        except ModbusException as e:
            error_msg = f"Modbus exception: {e}"
            _logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error reading setpoint: {e}"
            _logger.error(error_msg)
            return False, None, error_msg


# Global client instance
_client: Optional[NeasmartModbusClient] = None


def get_client(gateway_host: str = "192.168.1.200", gateway_port: int = 502, 
               neasmart_slave_id: int = 240) -> NeasmartModbusClient:
    """
    Get or create the global Neasmart Modbus client instance.
    
    Args:
        gateway_host: IP address of Waveshare gateway
        gateway_port: Port of Waveshare gateway
        neasmart_slave_id: Modbus slave ID of Neasmart device
        
    Returns:
        NeasmartModbusClient: Global client instance
    """
    global _client
    if _client is None:
        _client = NeasmartModbusClient(gateway_host, gateway_port, neasmart_slave_id)
    return _client

