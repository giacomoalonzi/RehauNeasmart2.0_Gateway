#!/usr/bin/env python3
"""
Modbus Manager for Rehau Neasmart Gateway.
Provides thread-safe access to Modbus context with circuit breaker pattern.
"""

import threading
import time
import logging
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus import __version__ as pymodbus_version
from pymodbus.device import ModbusDeviceIdentification

from database import DatabaseManager, get_database_manager
import const
import dpt_9001

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failures exceeded threshold
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    half_open_max_calls: int = 3


class ModbusException(Exception):
    """Base exception for Modbus operations"""
    pass


class ModbusReadError(ModbusException):
    """Raised when Modbus read operation fails"""
    pass


class ModbusWriteError(ModbusException):
    """Raised when Modbus write operation fails"""
    pass


class CircuitBreakerOpen(ModbusException):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """Circuit breaker implementation for Modbus operations"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        self._lock = threading.RLock()
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                else:
                    raise CircuitBreakerOpen(
                        f"Circuit breaker is OPEN. Waiting for recovery timeout. "
                        f"Last failure: {self.last_failure_time}"
                    )
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure.total_seconds() > self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.config.half_open_max_calls:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker closed after successful recovery")
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker reopened due to failure in half-open state")
        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None
        }


class ThreadSafeDataBlock(ModbusSequentialDataBlock):
    """Thread-safe Modbus data block with database backing"""
    
    def __init__(self, database_manager: DatabaseManager, start_address: int = 0):
        self.db_manager = database_manager
        self._lock = threading.RLock()
        
        # Initialize with values from database
        initial_values = self._load_initial_values()
        super().__init__(start_address, initial_values)
    
    def _load_initial_values(self) -> List[int]:
        """Load initial values from database"""
        # Load all 65536 registers
        return self.db_manager.get_registers(0, 65536)
    
    def setValues(self, address: int, values: List[int]) -> None:
        """Set values with database persistence"""
        with self._lock:
            if not isinstance(values, list):
                values = [values]
            
            # Update in-memory values
            super().setValues(address, values)
            
            # Persist to database
            try:
                self.db_manager.set_registers(address, values)
            except Exception as e:
                logger.error(f"Failed to persist values to database: {e}")
                # Continue operation even if database fails
    
    def getValues(self, address: int, count: int = 1) -> List[int]:
        """Get values from database with thread safety"""
        with self._lock:
            try:
                # Always read from database to get the latest values
                return self.db_manager.get_registers(address, count)
            except Exception as e:
                logger.error(f"Failed to read from database at {address}: {e}")
                # Fallback to in-memory values if database fails
                return super().getValues(address, count)


class ModbusManager:
    """
    Thread-safe Modbus context manager with circuit breaker protection.
    """
    
    def __init__(self, 
                 slave_id: int,
                 database_manager: Optional[DatabaseManager] = None,
                 circuit_breaker_config: Optional[CircuitBreakerConfig] = None):
        self.slave_id = slave_id
        self.db_manager = database_manager or get_database_manager()
        self.circuit_breaker = CircuitBreaker(
            circuit_breaker_config or CircuitBreakerConfig()
        )
        self.last_known_setpoints = {} # Cache for last good setpoints
        
        self._lock = threading.RLock()
        self._context = None
        self._data_block = None
        
        # Initialize Modbus context
        self._initialize_context()
    
    def _initialize_context(self) -> None:
        """Initialize Modbus server context"""
        try:
            # Create a data block for each slave
            self._data_block_main = ThreadSafeDataBlock(
                self.db_manager,
                const.REGS_STARTING_ADDR
            )
            # Create a dummy data block for the secondary slave to avoid errors
            self._data_block_secondary = ModbusSequentialDataBlock(0, [0] * 65536)

            # Create a slave context for each slave
            slave_context_main = ModbusSlaveContext(
                di=None, co=None, hr=self._data_block_main, ir=None
            )
            slave_context_secondary = ModbusSlaveContext(
                di=None, co=None, hr=self._data_block_secondary, ir=None
            )

            # Create server context with multiple slaves
            self._context = ModbusServerContext(
                slaves={
                    const.NEASMART_SLAVE_ADDRESS_PRIMARY: slave_context_main,
                    const.NEASMART_SLAVE_ADDRESS_SECONDARY: slave_context_secondary,
                },
                single=False
            )

            logger.info(f"Modbus context initialized for slaves: {const.NEASMART_SLAVE_ADDRESS_PRIMARY}, {const.NEASMART_SLAVE_ADDRESS_SECONDARY}")

        except Exception as e:
            logger.error(f"Failed to initialize Modbus context: {e}")
            raise ModbusException(f"Context initialization failed: {e}")
    
    def get_context(self) -> ModbusServerContext:
        """Get Modbus server context"""
        return self._context
    
    def get_identity(self) -> ModbusDeviceIdentification:
        """Get Modbus device identification"""
        return ModbusDeviceIdentification(
            info_name={
                "VendorName": "Rehau Neasmart Gateway",
                "ProductCode": "RNG",
                "VendorUrl": "https://github.com/your-repo",
                "ProductName": "Rehau Neasmart 2.0 Gateway",
                "ModelName": "Gateway",
                "MajorMinorRevision": pymodbus_version,
            }
        )
    
    def _is_zone_register(self, address: int) -> bool:
        """Check if an address belongs to a zone register."""
        if not (100 <= address < 4900):
            return False

        offset = address % const.ZONE_ID_MULTIPLIER
        if offset == 0:
            base_addr = address
        elif offset in [const.ZONE_SETPOINT_ADDR_OFFSET, const.ZONE_TEMP_ADDR_OFFSET, const.ZONE_RH_ADDR_OFFSET]:
            base_addr = address - offset
        else:
            return False

        zone_id_part = (base_addr % const.ZONE_BASE_ID_MULTIPLIER) // const.ZONE_ID_MULTIPLIER
        base_id_part = base_addr // const.ZONE_BASE_ID_MULTIPLIER

        if (1 <= zone_id_part <= 12) and (0 <= base_id_part < 4):
            return True
        
        return False

    def _validate_and_filter_read_data(self, address: int, values: List[int]) -> List[int]:
        """Validate data read from Modbus and fall back to DB if invalid."""
        if not values or len(values) > 1:
            return values
            
        original_value = values[0]

        is_invalid = False
        log_reason = ""

        if address in [const.GLOBAL_OP_STATE_ADDR, const.GLOBAL_OP_MODE_ADDR]:
            if original_value == 0:
                is_invalid = True
                log_reason = "global state/mode is zero"
        
        elif self._is_zone_register(address):
            offset = address % const.ZONE_ID_MULTIPLIER
            if offset == 0:  # Zone state
                if original_value == 0:
                    is_invalid = True
                    log_reason = "zone state is zero"
            elif offset == const.ZONE_SETPOINT_ADDR_OFFSET:  # Zone setpoint
                unpacked = dpt_9001.unpack_dpt9001(original_value)
                if unpacked is None or not (5.0 <= unpacked <= 40.0):
                    is_invalid = True
                    log_reason = f"zone setpoint out of range (unpacked: {unpacked})"
            elif offset == const.ZONE_TEMP_ADDR_OFFSET:  # Zone temperature
                unpacked = dpt_9001.unpack_dpt9001(original_value)
                if unpacked is None or unpacked == 0.0: # Treat 0.0 as a likely invalid startup value
                    is_invalid = True
                    log_reason = f"zone temperature is invalid or zero (unpacked: {unpacked})"
            elif offset == const.ZONE_RH_ADDR_OFFSET:  # Zone humidity
                if original_value == 0:
                    is_invalid = True
                    log_reason = "zone humidity is zero"

        if not is_invalid:
            return values

        logger.warning(f"Invalid value read for {address} (raw: {original_value}), reason: {log_reason}. Attempting to use cache.")
        try:
            if cached_values := self.db_manager.get_registers(address, 1):
                cached_value = cached_values[0]
                if cached_value != original_value:
                    logger.warning(f"Using cached value {cached_value} for register {address}.")
                    return [cached_value]
                else:
                    logger.warning(f"Cached value for {address} is the same as the invalid one, using original.")
            else:
                logger.warning(f"No cached value found for register {address}.")
        except Exception as e:
            logger.error(f"Error retrieving cached value for {address}: {e}")
            
        return values
    
    def read_registers(self, address: int, count: int = 1, update_db: bool = True) -> List[int]:
        """Read holding registers with circuit breaker protection"""
        def _read():
            with self._lock:
                if not self._context:
                    raise ModbusReadError("Modbus context not initialized")
                
                try:
                    slave_context = self._context[self.slave_id]
                    return slave_context.getValues(
                        const.READ_HR_CODE,
                        address,
                        count=count
                    )
                except Exception as e:
                    logger.error(f"Failed to read registers at {address}: {e}")
                    raise ModbusReadError(f"Read failed at address {address}: {e}")
        
        try:
            values = self.circuit_breaker.call(_read)

            validated_values = self._validate_and_filter_read_data(address, values)

            if update_db:
                self.db_manager.set_registers(address, validated_values)
            return validated_values
        except CircuitBreakerOpen:
            # Return cached values from database when circuit is open
            logger.warning(f"Circuit breaker open, returning cached values for address {address}")
            return self.db_manager.get_registers(address, count)
    
    def write_registers(self, address: int, values: List[int]) -> None:
        """Write holding registers with circuit breaker protection"""
        def _write():
            with self._lock:
                if not self._context:
                    raise ModbusWriteError("Modbus context not initialized")
                
                try:
                    # Get the correct data block from the context
                    slave_context = self._context[self.slave_id]
                    data_block = slave_context.store.get('h')

                    if not data_block:
                        raise ModbusWriteError("Holding register data block not found")

                    # Use the block's setValues to trigger the update
                    data_block.setValues(address, values)
                    
                except Exception as e:
                    logger.error(f"Failed to write registers at {address}: {e}")
                    raise ModbusWriteError(f"Write failed at address {address}: {e}")
        
        try:
            self.circuit_breaker.call(_write)
        except CircuitBreakerOpen:
            # Store values in database even when circuit is open
            logger.warning(f"Circuit breaker open, storing values in database for address {address}")
            self.db_manager.set_registers(address, values)
            raise
    
    def read_register(self, address: int, update_db: bool = True) -> int:
        """Read single holding register"""
        return self.read_registers(address, 1, update_db=update_db)[0]
    
    def write_register(self, address: int, value: int) -> None:
        """Write single holding register"""
        self.write_registers(address, [value])
    
    def sync_from_bus(self, start_address: int = 0, count: int = 65536) -> None:
        """Sync database with current bus values"""
        logger.info(f"Starting bus sync for {count} registers from address {start_address}")
        
        batch_size = 100  # Read in batches to avoid timeouts
        synced = 0
        
        with self._lock:
            for addr in range(start_address, start_address + count, batch_size):
                try:
                    batch_count = min(batch_size, start_address + count - addr)
                    values = self.read_registers(addr, batch_count)
                    self.db_manager.set_registers(addr, values)
                    synced += batch_count
                    
                    if synced % 1000 == 0:
                        logger.info(f"Synced {synced}/{count} registers")
                        
                except Exception as e:
                    logger.error(f"Failed to sync batch at address {addr}: {e}")
        
        logger.info(f"Bus sync completed. Synced {synced} registers")
    
    def get_status(self) -> Dict[str, Any]:
        """Get manager status for monitoring"""
        return {
            "slave_id": self.slave_id,
            "context_initialized": self._context is not None,
            "circuit_breaker": self.circuit_breaker.get_status(),
            "database": self.db_manager.get_status()
        }
    
    def close(self) -> None:
        """Cleanup resources"""
        logger.info("Closing Modbus manager")
        # Context cleanup if needed


# Singleton instance holder
_modbus_manager: Optional[ModbusManager] = None
_manager_lock = threading.Lock()


def get_modbus_manager(slave_id: int = None, **kwargs) -> ModbusManager:
    """Get or create singleton ModbusManager instance"""
    global _modbus_manager
    
    # Log every attempt to get the manager
    logger.info(f"get_modbus_manager called. Requested slave_id: {slave_id}. Current singleton is for: {_modbus_manager.slave_id if _modbus_manager else 'None'}")
    
    with _manager_lock:
        if _modbus_manager is None:
            if slave_id is None:
                raise ValueError(f"slave_id must be provided for first initialization. Requested slave_id: {slave_id}")
            # Only allow slave_id 240 and 241
            if slave_id not in (240, 241):
                raise ValueError(
                    f"Invalid slave_id: {slave_id}. Only slave_id=240 and 241 are supported in this deployment."
                )
            _modbus_manager = ModbusManager(slave_id, **kwargs)
        return _modbus_manager


def close_modbus_manager() -> None:
    """Close and cleanup singleton ModbusManager instance"""
    global _modbus_manager
    
    with _manager_lock:
        if _modbus_manager:
            _modbus_manager.close()
            _modbus_manager = None 

logging.getLogger("pymodbus").setLevel(logging.WARNING) 