#!/usr/bin/env python3

import asyncio
import logging
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus import __version__ as pymodbus_version
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartAsyncSerialServer, StartAsyncTcpServer
from database import LockingPersistentDataBlock
import const

_logger = logging.getLogger(__name__)


def setup_server_context(datastore_path, slave_id=240):
    """
    Setup Modbus server context with persistent data block.
    
    Args:
        datastore_path (str): Path to the SQLite database file
        slave_id (int): Modbus slave ID (default: 240)
        
    Returns:
        ModbusServerContext: Configured server context
    """
    datablock = LockingPersistentDataBlock.create_lpdb(datastore_path)
    
    slave_context = {
        slave_id: ModbusSlaveContext(
            di=None,
            co=None,
            hr=datablock,
            ir=None,
        ),
        # Add slave ID 241 as well if needed
        241: ModbusSlaveContext(
            di=None,
            co=None,
            hr=datablock,
            ir=None,
        ),
    }

    return ModbusServerContext(slaves=slave_context, single=False)


async def run_modbus_server(server_context, server_addr, conn_type):
    """
    Run the Modbus server with specified configuration.
    
    Args:
        server_context (ModbusServerContext): Server context
        server_addr (tuple or str): Server address (tuple for TCP, string for serial)
        conn_type (str): Connection type ('tcp' or 'serial')
        
    Returns:
        Server instance
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
        return await StartAsyncTcpServer(
            context=server_context,
            identity=identity,
            address=server_addr,
            framer="socket",
            ignore_missing_slaves=True,
            broadcast_enable=True,
        )
    elif conn_type == "serial":
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


def start_modbus_server(config):
    """
    Start the Modbus server with configuration from config object.
    
    Args:
        config: Configuration object with server settings
    """
    context = setup_server_context(const.DATASTORE_PATH, config.slave_id)
    
    if config.server_type == "tcp":
        addr = (config.listen_address, config.listen_port)
    elif config.server_type == "serial":
        addr = config.listen_address
    else:
        _logger.critical("Unsupported server type")
        raise ValueError(f"Unsupported server type: {config.server_type}")

    return asyncio.run(run_modbus_server(context, addr, config.server_type))
