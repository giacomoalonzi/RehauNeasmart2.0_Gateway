#!/usr/bin/env python3

"""
Modbus Traffic Monitor

This module intercepts and logs all Modbus operations to understand
the communication pattern between the physical Neasmart device and our server.
"""

import logging
from datetime import datetime
from typing import Any, List
import threading

_logger = logging.getLogger(__name__)


class ModbusOperationLog:
    """Store information about a single Modbus operation."""
    
    def __init__(self, operation_type: str, slave_id: int, address: int, 
                 values: List[int] = None, count: int = None, source: str = "unknown"):
        self.timestamp = datetime.now()
        self.operation_type = operation_type  # "read" or "write"
        self.slave_id = slave_id
        self.address = address
        self.values = values if values is not None else []
        self.count = count
        self.source = source  # "api", "external", "internal"
    
    def __str__(self):
        ts = self.timestamp.strftime("%H:%M:%S.%f")[:-3]
        if self.operation_type == "write":
            values_str = f"values={self.values}" if len(self.values) <= 5 else f"values=[{len(self.values)} items]"
            return f"[{ts}] {self.source:8s} WRITE slave={self.slave_id} addr={self.address:5d} {values_str}"
        else:
            return f"[{ts}] {self.source:8s} READ  slave={self.slave_id} addr={self.address:5d} count={self.count}"


class ModbusMonitor:
    """
    Monitor and log all Modbus operations.
    
    This class can be used to wrap a ModbusDataBlock and intercept
    all read/write operations for debugging and analysis.
    """
    
    def __init__(self):
        self.operations: List[ModbusOperationLog] = []
        self.lock = threading.Lock()
        self.enabled = True
        self.log_to_console = True
        self.log_to_file = False
        self.log_file_path = "./data/modbus_traffic.log"
    
    def log_operation(self, op: ModbusOperationLog):
        """Log a Modbus operation."""
        if not self.enabled:
            return
        
        with self.lock:
            self.operations.append(op)
            
            # Log to console
            if self.log_to_console:
                _logger.info(f"[MODBUS MONITOR] {op}")
            
            # Log to file
            if self.log_to_file:
                try:
                    with open(self.log_file_path, 'a') as f:
                        f.write(f"{op}\n")
                except Exception as e:
                    _logger.error(f"Failed to write to monitor log file: {e}")
    
    def log_read(self, slave_id: int, address: int, count: int, source: str = "unknown"):
        """Log a read operation."""
        op = ModbusOperationLog("read", slave_id, address, count=count, source=source)
        self.log_operation(op)
    
    def log_write(self, slave_id: int, address: int, values: List[int], source: str = "unknown"):
        """Log a write operation."""
        op = ModbusOperationLog("write", slave_id, address, values=values, source=source)
        self.log_operation(op)
    
    def get_operations(self, last_n: int = None, operation_type: str = None, 
                      address: int = None, source: str = None) -> List[ModbusOperationLog]:
        """
        Get filtered operations.
        
        Args:
            last_n: Return only the last N operations
            operation_type: Filter by "read" or "write"
            address: Filter by register address
            source: Filter by source ("api", "external", "internal")
        """
        with self.lock:
            ops = self.operations.copy()
        
        # Apply filters
        if operation_type:
            ops = [op for op in ops if op.operation_type == operation_type]
        if address is not None:
            ops = [op for op in ops if op.address == address]
        if source:
            ops = [op for op in ops if op.source == source]
        
        # Return last N
        if last_n:
            ops = ops[-last_n:]
        
        return ops
    
    def get_statistics(self) -> dict:
        """Get statistics about Modbus operations."""
        with self.lock:
            ops = self.operations.copy()
        
        stats = {
            "total_operations": len(ops),
            "reads": len([op for op in ops if op.operation_type == "read"]),
            "writes": len([op for op in ops if op.operation_type == "write"]),
            "by_source": {},
            "addresses_written": set(),
            "addresses_read": set(),
        }
        
        # Count by source
        for op in ops:
            if op.source not in stats["by_source"]:
                stats["by_source"][op.source] = {"reads": 0, "writes": 0}
            if op.operation_type == "read":
                stats["by_source"][op.source]["reads"] += 1
                stats["addresses_read"].add(op.address)
            else:
                stats["by_source"][op.source]["writes"] += 1
                stats["addresses_written"].add(op.address)
        
        # Convert sets to sorted lists
        stats["addresses_written"] = sorted(list(stats["addresses_written"]))
        stats["addresses_read"] = sorted(list(stats["addresses_read"]))
        
        return stats
    
    def clear(self):
        """Clear all logged operations."""
        with self.lock:
            self.operations.clear()
        _logger.info("[MODBUS MONITOR] Cleared all logged operations")
    
    def print_summary(self):
        """Print a summary of Modbus operations."""
        stats = self.get_statistics()
        
        print("\n" + "=" * 60)
        print("MODBUS TRAFFIC SUMMARY")
        print("=" * 60)
        print(f"Total operations: {stats['total_operations']}")
        print(f"  Reads:  {stats['reads']}")
        print(f"  Writes: {stats['writes']}")
        print()
        print("By source:")
        for source, counts in stats["by_source"].items():
            print(f"  {source:10s} - Reads: {counts['reads']:4d}, Writes: {counts['writes']:4d}")
        print()
        print(f"Addresses written ({len(stats['addresses_written'])}): {stats['addresses_written'][:20]}...")
        print(f"Addresses read ({len(stats['addresses_read'])}): {stats['addresses_read'][:20]}...")
        print("=" * 60 + "\n")


# Global monitor instance
_monitor = ModbusMonitor()


def get_monitor() -> ModbusMonitor:
    """Get the global Modbus monitor instance."""
    return _monitor

