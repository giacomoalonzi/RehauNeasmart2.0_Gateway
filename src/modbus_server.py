#!/usr/bin/env python3

import logging
import os
import threading
from typing import Tuple, Union

from pymodbus import __version__ as pymodbus_version
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartAsyncSerialServer, StartAsyncTcpServer
from sqlitedict import SqliteDict

import const

_logger = logging.getLogger(__name__)


class LockingPersistentDataBlock(ModbusSequentialDataBlock):
    """
    Thread-safe Modbus data block with persistent storage.
    
    This class extends ModbusSequentialDataBlock to provide:
    - Thread-safe read/write operations using locks
    - Persistent storage using SQLite
    - Automatic initialization of register space
    """
    
    lock = threading.Lock()
    reg_dict = None

    def setValues(self, address, value):
        """
        Set register values with thread safety and persistence.
        
        Args:
            address (int): Starting register address
            value (int or list): Value(s) to set
        """
        with self.lock:
            if not isinstance(value, list):
                value = [value]
            for k in range(0, len(value)):
                self.reg_dict[address + k] = value[k]
            super().setValues(address, value)

    def getValues(self, address, count=1):
        """
        Get register values with thread safety.
        
        Args:
            address (int): Starting register address
            count (int): Number of registers to read
            
        Returns:
            list: Register values
        """
        with self.lock:
            result = super().getValues(address, count=count)
            return result

    @classmethod
    def create_lpdb(cls, reg_datastore_path: str):
        """
        Create a LockingPersistentDataBlock instance.
        
        Initializes the SQLite database if it doesn't exist,
        populating all 65536 registers with zero values.
        
        Args:
            reg_datastore_path (str): Path to SQLite database file
            
        Returns:
            LockingPersistentDataBlock: Initialized data block instance
        """
        if not os.path.exists(reg_datastore_path):
            _logger.warning(f"Initialising DB at {reg_datastore_path}")
            init_dict = SqliteDict(
                reg_datastore_path,
                tablename=const.SQLITEDICT_REGS_TABLE,
                autocommit=False
            )
            for k in range(0, 65536):
                init_dict[k] = 0
            init_dict.commit()
            init_dict.close()

        _logger.warning(f"Using DB at {reg_datastore_path}")
        cls.reg_dict = SqliteDict(
            reg_datastore_path,
            tablename=const.SQLITEDICT_REGS_TABLE,
            autocommit=True
        )

        sorted_dict = dict(sorted(cls.reg_dict.iteritems(), key=lambda x: int(x[0])))

        return cls(const.REGS_STARTING_ADDR, list(sorted_dict.values()))


def setup_server_context(datastore_path: str, slave_id: int) -> ModbusServerContext:
    """
    Setup Modbus server context with persistent data storage.
    
    Creates a server context with multiple slave IDs sharing the same data block.
    
    Args:
        datastore_path (str): Path to SQLite database file
        slave_id (int): Primary slave ID to configure
        
    Returns:
        ModbusServerContext: Configured Modbus server context
    """
    datablock = LockingPersistentDataBlock.create_lpdb(datastore_path)
    
    # Create slave contexts with the same datablock
    slave_context = {
        slave_id: ModbusSlaveContext(
            di=None,
            co=None,
            hr=datablock,
            ir=None,
        ),
        # Add slave ID 241 as well for compatibility
        241: ModbusSlaveContext(
            di=None,
            co=None,
            hr=datablock,
            ir=None,
        ),
    }

    return ModbusServerContext(slaves=slave_context, single=False)


async def run_modbus_server(
    server_context: ModbusServerContext,
    server_addr: Union[Tuple[str, int], str],
    conn_type: str
):
    """
    Run the Modbus server (TCP or Serial).
    
    Args:
        server_context (ModbusServerContext): Configured server context
        server_addr (tuple or str): Server address (tuple for TCP, string for serial)
        conn_type (str): Connection type ('tcp' or 'serial')
        
    Returns:
        Server instance
        
    Raises:
        ValueError: If connection type is invalid
    """
    identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "Pymodbus",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/pymodbus-dev/pymodbus/",
            "ProductName": "Pymodbus Server",
            "ModelName": "Pymodbus Server",
            "MajorMinorRevision": pymodbus_version,
        }
    )
    
    if conn_type == "tcp":
        _logger.info(f"Starting Modbus TCP server on {server_addr}")
        return await StartAsyncTcpServer(
            context=server_context,
            identity=identity,
            address=server_addr,
            framer="socket",
            ignore_missing_slaves=True,
            broadcast_enable=True,
        )
    elif conn_type == "serial":
        _logger.info(f"Starting Modbus Serial server on {server_addr}")
        return await StartAsyncSerialServer(
            context=server_context,
            identity=identity,
            port=server_addr,
            framer="rtu",
            stopbits=const.NEASMART_SYSBUS_STOP_BITS,
            bytesize=const.NEASMART_SYSBUS_DATA_BITS,
            parity=const.NEASMART_SYSBUS_PARITY,
            ignore_missing_slaves=True,
            broadcast_enable=True,
        )
    else:
        raise ValueError(f"Unsupported connection type: {conn_type}")
