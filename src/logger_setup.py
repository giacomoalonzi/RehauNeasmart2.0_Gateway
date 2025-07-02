#!/usr/bin/env python3
"""
Logging setup for Rehau Neasmart Gateway.
Provides structured logging with rotation and multiple handlers.
"""

import logging
import logging.handlers
import sys
import os
from typing import Optional, Dict
from pythonjsonlogger import jsonlogger
import time

from config import LoggingConfig


class ContextFilter(logging.Filter):
    """Add context information to log records"""
    
    def __init__(self, app_name: str = "neasmart-gateway"):
        super().__init__()
        self.app_name = app_name
        self.hostname = os.environ.get('HOSTNAME', 'unknown')
        self.environment = os.environ.get('ENVIRONMENT', 'production')
    
    def filter(self, record):
        record.app_name = self.app_name
        record.hostname = self.hostname
        record.environment = self.environment
        return True


def setup_logging(config: LoggingConfig, app_name: str = "neasmart-gateway") -> None:
    """
    Setup logging configuration with structured output.
    
    Args:
        config: Logging configuration
        app_name: Application name for context
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create formatters
    if os.environ.get('LOG_FORMAT') == 'json':
        # JSON formatter for production
        json_formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            timestamp=True,
            rename_fields={'levelname': 'level', 'asctime': 'timestamp'}
        )
        formatter = json_formatter
    else:
        # Standard formatter for development
        formatter = logging.Formatter(config.format)
    
    # Add context filter
    context_filter = ContextFilter(app_name)
    
    # Console handler
    if config.enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(context_filter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if config.enable_file and config.file_path:
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(config.file_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                filename=config.file_path,
                maxBytes=config.max_file_size,
                backupCount=config.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.addFilter(context_filter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            logging.error(f"Failed to setup file logging: {e}")
    
    # Syslog handler (optional)
    if os.environ.get('ENABLE_SYSLOG', 'false').lower() == 'true':
        try:
            syslog_address = os.environ.get('SYSLOG_ADDRESS', '/dev/log')
            if ':' in syslog_address:
                # Network syslog
                host, port = syslog_address.split(':')
                syslog_handler = logging.handlers.SysLogHandler(
                    address=(host, int(port))
                )
            else:
                # Local syslog
                syslog_handler = logging.handlers.SysLogHandler(
                    address=syslog_address
                )
            
            syslog_handler.setFormatter(formatter)
            syslog_handler.addFilter(context_filter)
            root_logger.addHandler(syslog_handler)
        except Exception as e:
            logging.error(f"Failed to setup syslog: {e}")
    
    # Configure specific loggers
    configure_library_loggers()
    
    logging.info(f"Logging configured: level={config.level}, handlers={len(root_logger.handlers)}")

    # Throttle pymodbus 'requested slave does not exist' errors to max once every 120s
    pymodbus_logger = logging.getLogger('pymodbus')
    orig_error = pymodbus_logger.error
    _last_ts = {'t': 0}
    def filtered_error(msg, *args, **kwargs):
        text = str(msg)
        if 'requested slave does not exist' in text.lower():
            now = time.time()
            if now - _last_ts['t'] < 120:
                return
            _last_ts['t'] = now
            pymodbus_logger.warning(text)
            return
        orig_error(msg, *args, **kwargs)
    pymodbus_logger.error = filtered_error


def configure_library_loggers():
    """Configure logging levels for third-party libraries"""
    # Reduce noise from libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlitedict').setLevel(logging.WARNING)
    
    # Modbus logging
    logging.getLogger('pymodbus').setLevel(logging.INFO)
    logging.getLogger('pymodbus.client').setLevel(logging.WARNING)
    logging.getLogger('pymodbus.transaction').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class LoggerContext:
    """Context manager for temporary logger configuration changes"""
    
    def __init__(self, logger_name: str, level: Optional[str] = None, 
                 handler: Optional[logging.Handler] = None):
        self.logger = logging.getLogger(logger_name)
        self.original_level = self.logger.level
        self.original_handlers = self.logger.handlers.copy()
        self.new_level = level
        self.new_handler = handler
    
    def __enter__(self):
        if self.new_level:
            self.logger.setLevel(getattr(logging, self.new_level.upper()))
        if self.new_handler:
            self.logger.addHandler(self.new_handler)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)
        if self.new_handler:
            self.logger.removeHandler(self.new_handler)


def log_exception(logger: logging.Logger, exc: Exception, 
                  message: str = "Exception occurred") -> None:
    """
    Log an exception with full traceback.
    
    Args:
        logger: Logger instance
        exc: Exception to log
        message: Additional context message
    """
    logger.exception(f"{message}: {type(exc).__name__}: {str(exc)}")


def create_audit_logger(name: str = "audit") -> logging.Logger:
    """
    Create a separate audit logger for security events.
    
    Args:
        name: Logger name
    
    Returns:
        Configured audit logger
    """
    audit_logger = logging.getLogger(f"{name}.audit")
    audit_logger.setLevel(logging.INFO)
    
    # Audit logs always go to file
    audit_file = os.environ.get('AUDIT_LOG_FILE', './data/audit.log')
    audit_dir = os.path.dirname(audit_file)
    if audit_dir:
        os.makedirs(audit_dir, exist_ok=True)
    
    audit_handler = logging.handlers.RotatingFileHandler(
        filename=audit_file,
        maxBytes=10485760,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    
    # Use JSON format for audit logs
    audit_formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(user)s %(action)s %(resource)s',
        timestamp=True
    )
    audit_handler.setFormatter(audit_formatter)
    
    audit_logger.addHandler(audit_handler)
    audit_logger.propagate = False  # Don't propagate to root logger
    
    return audit_logger


def log_api_request(logger: logging.Logger, method: str, path: str, 
                    status_code: int, duration_ms: float, 
                    user: Optional[str] = None) -> None:
    """
    Log API request with structured data.
    
    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        user: User identifier (if authenticated)
    """
    extra = {
        'method': method,
        'path': path,
        'status_code': status_code,
        'duration_ms': duration_ms,
        'user': user or 'anonymous'
    }
    
    if status_code >= 500:
        logger.error(f"API request failed: {method} {path}", extra=extra)
    elif status_code >= 400:
        logger.warning(f"API request error: {method} {path}", extra=extra)
    else:
        logger.info(f"API request: {method} {path}", extra=extra) 