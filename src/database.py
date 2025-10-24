#!/usr/bin/env python3

import logging
import os
import threading
from pymodbus.datastore import ModbusSequentialDataBlock
from sqlitedict import SqliteDict
import const

_logger = logging.getLogger(__name__)


class LockingPersistentDataBlock(ModbusSequentialDataBlock):
    """
    Custom Modbus data block with SQLite persistence and thread-safe operations.
    Extends ModbusSequentialDataBlock to provide persistent storage using SQLite.
    """
    
    lock = threading.Lock()
    reg_dict = None

    def setValues(self, address, value):
        """
        Set values in the data block with thread-safe persistence.
        
        Args:
            address (int): Starting address for the values
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
        Get values from the data block with thread-safe access.
        
        Args:
            address (int): Starting address
            count (int): Number of values to retrieve
            
        Returns:
            list: Retrieved values
        """
        with self.lock:
            result = super().getValues(address, count=count)
            return result

    @classmethod
    def create_lpdb(cls, reg_datastore_path):
        """
        Create and initialize a LockingPersistentDataBlock with SQLite backend.
        
        Args:
            reg_datastore_path (str): Path to the SQLite database file
            
        Returns:
            LockingPersistentDataBlock: Initialized data block instance
        """
        if not os.path.exists(reg_datastore_path):
            _logger.warning("Initialising DB at {}".format(reg_datastore_path))
            init_dict = SqliteDict(
                reg_datastore_path, 
                tablename=const.SQLITEDICT_REGS_TABLE, 
                autocommit=False
            )
            for k in range(0, 65536):
                init_dict[k] = 0
            init_dict.commit()
            init_dict.close()

        _logger.warning("Using DB at {}".format(reg_datastore_path))
        cls.reg_dict = SqliteDict(
            reg_datastore_path, 
            tablename=const.SQLITEDICT_REGS_TABLE, 
            autocommit=True
        )

        sorted_dict = dict(sorted(cls.reg_dict.iteritems(), key=lambda x: int(x[0])))

        return cls(const.REGS_STARTING_ADDR, list(sorted_dict.values()))
