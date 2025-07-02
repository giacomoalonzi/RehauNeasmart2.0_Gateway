#!/usr/bin/env python3
"""
Database abstraction layer for Rehau Neasmart Gateway.
Provides thread-safe access to register storage with automatic retry and fallback mechanisms.
"""

import threading
import time
import logging
from typing import Optional, Dict, Any, List, Union
from contextlib import contextmanager
from pathlib import Path
import os
from sqlitedict import SqliteDict
from collections import defaultdict

logger = logging.getLogger(__name__)


class DatabaseException(Exception):
    """Base exception for database operations"""
    pass


class DatabaseConnectionError(DatabaseException):
    """Raised when database connection fails"""
    pass


class DatabaseOperationError(DatabaseException):
    """Raised when database operation fails"""
    pass


class RetryPolicy:
    """Configuration for retry behavior"""
    def __init__(self, max_attempts: int = 3, base_delay: float = 0.1, max_delay: float = 1.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def get_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)


class InMemoryFallback:
    """In-memory fallback storage when database is unavailable"""
    def __init__(self):
        self._data: Dict[int, int] = defaultdict(int)
        self._lock = threading.RLock()
        self._dirty = False
    
    def get(self, key: int, default: int = 0) -> int:
        with self._lock:
            return self._data.get(key, default)
    
    def set(self, key: int, value: int) -> None:
        with self._lock:
            self._data[key] = value
            self._dirty = True
    
    def get_range(self, start: int, count: int) -> List[int]:
        with self._lock:
            return [self._data.get(start + i, 0) for i in range(count)]
    
    def set_range(self, start: int, values: List[int]) -> None:
        with self._lock:
            for i, value in enumerate(values):
                self._data[start + i] = value
            self._dirty = True
    
    def is_dirty(self) -> bool:
        return self._dirty
    
    def get_all_data(self) -> Dict[int, int]:
        with self._lock:
            return dict(self._data)
    
    def clear(self) -> None:
        """Clears all data from the fallback storage."""
        with self._lock:
            self._data.clear()
            self._dirty = True
    
    def clear_dirty_flag(self) -> None:
        self._dirty = False


class DatabaseManager:
    """
    Thread-safe database manager with automatic retry and fallback.
    Provides robust access to register storage.
    """
    
    def __init__(self, 
                 db_path: str,
                 table_name: str = "holding_registers",
                 retry_policy: Optional[RetryPolicy] = None,
                 enable_fallback: bool = True):
        self.db_path = db_path
        self.table_name = table_name
        self.retry_policy = retry_policy or RetryPolicy()
        self.enable_fallback = enable_fallback
        
        self._lock = threading.RLock()
        self._db: Optional[SqliteDict] = None
        self._fallback = InMemoryFallback() if enable_fallback else None
        self._connection_healthy = False
        self._last_health_check = 0
        self._health_check_interval = 30  # seconds
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database connection with proper error handling"""
        try:
            # Ensure directory exists
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # Check if database exists
            db_exists = os.path.exists(self.db_path)
            
            if not db_exists:
                logger.info(f"Creating new database at {self.db_path}")
                self._create_initial_database()
            else:
                logger.info(f"Using existing database at {self.db_path}")
                self._connect()
                
            self._connection_healthy = True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self._connection_healthy = False
            if not self.enable_fallback:
                raise DatabaseConnectionError(f"Database initialization failed: {e}")
    
    def _create_initial_database(self) -> None:
        """Create initial database with all registers initialized to 0"""
        try:
            with SqliteDict(self.db_path, tablename=self.table_name, autocommit=False) as db:
                logger.info("Initializing 65536 registers to 0")
                for i in range(0, 65536):
                    db[i] = 0
                db.commit()
            self._connect()
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to create initial database: {e}")
    
    def _connect(self) -> None:
        """Establish database connection"""
        try:
            self._db = SqliteDict(self.db_path, tablename=self.table_name, autocommit=True)
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {e}")
    
    def _check_connection_health(self) -> bool:
        """Check if database connection is healthy"""
        current_time = time.time()
        
        # Rate limit health checks
        if current_time - self._last_health_check < self._health_check_interval:
            return self._connection_healthy
        
        self._last_health_check = current_time
        
        try:
            if self._db is None:
                self._connect()
            
            # Try a simple operation
            _ = self._db.get(0, 0)
            self._connection_healthy = True
            
            # Sync fallback data if it was used
            if self._fallback and self._fallback.is_dirty():
                self._sync_fallback_to_database()
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            self._connection_healthy = False
            
        return self._connection_healthy
    
    def _sync_fallback_to_database(self) -> None:
        """Sync in-memory fallback data to database when connection is restored"""
        if not self._fallback or not self._fallback.is_dirty():
            return
        
        try:
            logger.info("Syncing fallback data to database")
            data = self._fallback.get_all_data()
            
            with self._lock:
                for key, value in data.items():
                    self._db[key] = value
                
            self._fallback.clear_dirty_flag()
            logger.info(f"Successfully synced {len(data)} values to database")
            
        except Exception as e:
            logger.error(f"Failed to sync fallback data: {e}")
    
    def _execute_with_retry(self, operation, *args, **kwargs):
        """Execute operation with retry logic"""
        last_exception = None
        
        for attempt in range(self.retry_policy.max_attempts):
            try:
                # Check connection health before operation
                if not self._check_connection_health() and not self.enable_fallback:
                    raise DatabaseConnectionError("Database connection unhealthy")
                
                # Try the operation
                if self._connection_healthy and self._db:
                    return operation(*args, **kwargs)
                elif self.enable_fallback:
                    # Use fallback if database is unavailable
                    raise DatabaseOperationError("Using fallback")
                    
            except Exception as e:
                last_exception = e
                logger.warning(f"Database operation failed (attempt {attempt + 1}/{self.retry_policy.max_attempts}): {e}")
                
                if attempt < self.retry_policy.max_attempts - 1:
                    delay = self.retry_policy.get_delay(attempt)
                    time.sleep(delay)
                    
                    # Try to reconnect on connection errors
                    if isinstance(e, (DatabaseConnectionError, AttributeError)):
                        try:
                            self._connect()
                        except Exception:
                            pass
        
        # All retries failed
        if self.enable_fallback:
            logger.warning("All database attempts failed, using in-memory fallback")
            return None  # Signal to use fallback
        else:
            raise DatabaseOperationError(f"Operation failed after {self.retry_policy.max_attempts} attempts: {last_exception}")
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        with self._lock:
            if self._connection_healthy and self._db:
                self._db.autocommit = False
                try:
                    yield self
                    self._db.commit()
                finally:
                    self._db.autocommit = True
            else:
                # In fallback mode, transactions are no-op
                yield self
    
    def get_register(self, address: int, default: int = 0) -> int:
        """Get a single register value with fallback support"""
        with self._lock:
            def _get():
                return self._db.get(address, default)
            
            result = self._execute_with_retry(_get)
            
            if result is None and self._fallback:
                return self._fallback.get(address, default)
            
            return result if result is not None else default
    
    def set_register(self, address: int, value: int) -> None:
        """Set a single register value with fallback support"""
        with self._lock:
            def _set():
                self._db[address] = value
            
            result = self._execute_with_retry(_set)
            
            if result is None and self._fallback:
                self._fallback.set(address, value)
    
    def get_registers(self, start_address: int, count: int) -> List[int]:
        """Get multiple register values with fallback support"""
        with self._lock:
            def _get_range():
                return [self._db.get(start_address + i, 0) for i in range(count)]
            
            result = self._execute_with_retry(_get_range)
            
            if result is None and self._fallback:
                return self._fallback.get_range(start_address, count)
            
            return result if result is not None else [0] * count
    
    def set_registers(self, start_address: int, values: List[int]) -> None:
        """Set multiple register values with fallback support"""
        with self._lock:
            def _set_range():
                for i, value in enumerate(values):
                    self._db[start_address + i] = value
            
            result = self._execute_with_retry(_set_range)
            
            if result is None and self._fallback:
                self._fallback.set_range(start_address, values)
    
    def close(self) -> None:
        """Close database connection"""
        with self._lock:
            if self._db:
                try:
                    self._db.close()
                except Exception as e:
                    logger.error(f"Error closing database: {e}")
                finally:
                    self._db = None
                    self._connection_healthy = False
    
    def is_using_fallback(self) -> bool:
        """Check if currently using fallback"""
        return not self._connection_healthy and self.enable_fallback

    def get_status(self) -> Dict[str, Any]:
        """Get database status"""
        with self._lock:
            db_entries = 0
            if self._connection_healthy and self._db:
                try:
                    db_entries = len(list(self._db.keys()))
                except Exception as e:
                    logger.error(f"Could not get db entry count: {e}")
            
            return {
                "db_path": self.db_path,
                "healthy": self._connection_healthy,
                "using_fallback": self.is_using_fallback(),
                "last_health_check": self._last_health_check,
                "fallback_entries": len(self._fallback.get_all_data()) if self._fallback else 0,
                "db_entries": db_entries
            }
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Singleton instance holder
_database_manager: Optional[DatabaseManager] = None
_manager_lock = threading.Lock()


def get_database_manager(db_path: str = None, **kwargs) -> DatabaseManager:
    """Get or create singleton DatabaseManager instance"""
    global _database_manager
    
    with _manager_lock:
        if _database_manager is None:
            if db_path is None:
                raise ValueError("db_path must be provided for first initialization")
            _database_manager = DatabaseManager(db_path, **kwargs)
        
        return _database_manager


def close_database_manager() -> None:
    """Close and cleanup singleton DatabaseManager instance"""
    global _database_manager
    
    with _manager_lock:
        if _database_manager:
            _database_manager.close()
            _database_manager = None 