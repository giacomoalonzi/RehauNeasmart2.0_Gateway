#!/usr/bin/env python3
"""
Configuration management for Rehau Neasmart Gateway.
Supports both file-based and environment variable configuration with validation.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import ipaddress

logger = logging.getLogger(__name__)


class ServerType(str, Enum):
    """Supported server types"""
    TCP = "tcp"
    SERIAL = "serial"


class ConfigError(Exception):
    """Configuration related errors"""
    pass


@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: str = "./data/registers.db"
    table_name: str = "holding_registers"
    enable_fallback: bool = True
    retry_max_attempts: int = 3
    retry_base_delay: float = 0.1
    retry_max_delay: float = 1.0
    health_check_interval: int = 30


@dataclass
class ModbusConfig:
    """Modbus configuration"""
    slave_id: int = 240
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 60
    circuit_breaker_half_open_calls: int = 3
    sync_on_startup: bool = False
    sync_batch_size: int = 100


@dataclass
class ServerConfig:
    """Server configuration"""
    type: ServerType = ServerType.TCP
    address: str = "0.0.0.0"
    port: int = 502
    # Serial specific settings
    serial_port: str = "/dev/ttyUSB0"
    serial_baudrate: int = 38400
    serial_bytesize: int = 8
    serial_parity: str = "N"
    serial_stopbits: int = 1


@dataclass
class APIConfig:
    """API configuration"""
    host: str = "0.0.0.0"
    port: int = 5001
    enable_auth: bool = False
    api_key: Optional[str] = None
    jwt_secret: Optional[str] = None
    rate_limit_per_minute: int = 60
    enable_cors: bool = True
    cors_origins: list = field(default_factory=lambda: ["*"])
    request_timeout: int = 30
    max_request_size: int = 1048576  # 1MB
    temperature_unit: str = "C"  # "C" for Celsius, "F" for Fahrenheit


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = "./data/gateway.log"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True


@dataclass
class AppConfig:
    """Main application configuration"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    modbus: ModbusConfig = field(default_factory=ModbusConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    api: APIConfig = field(default_factory=APIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Feature flags
    enable_health_endpoint: bool = True
    enable_metrics: bool = True
    enable_swagger: bool = True
    debug_mode: bool = False
    zones: Dict[str, Any] = field(default_factory=dict)


class ConfigValidator:
    """Configuration validator"""
    
    @staticmethod
    def validate_ip_address(address: str) -> None:
        """Validate IP address"""
        if address not in ["0.0.0.0", "localhost", "127.0.0.1"]:
            try:
                ipaddress.ip_address(address)
            except ValueError:
                raise ConfigError(f"Invalid IP address: {address}")
    
    @staticmethod
    def validate_port(port: int) -> None:
        """Validate port number"""
        if not 1 <= port <= 65535:
            raise ConfigError(f"Invalid port number: {port}. Must be between 1 and 65535")
    
    @staticmethod
    def validate_slave_id(slave_id: int) -> None:
        """Validate Modbus slave ID"""
        if not 1 <= slave_id <= 247:
            raise ConfigError(f"Invalid slave ID: {slave_id}. Must be between 1 and 247")
    
    @staticmethod
    def validate_log_level(level: str) -> None:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level.upper() not in valid_levels:
            raise ConfigError(f"Invalid log level: {level}. Must be one of {valid_levels}")
    
    @classmethod
    def validate_config(cls, config: AppConfig) -> None:
        """Validate entire configuration"""
        # Validate server config
        cls.validate_ip_address(config.server.address)
        cls.validate_port(config.server.port)
        
        # Validate API config
        cls.validate_ip_address(config.api.host)
        cls.validate_port(config.api.port)
        
        # Validate Modbus config
        cls.validate_slave_id(config.modbus.slave_id)
        
        # Validate logging config
        cls.validate_log_level(config.logging.level)
        
        # Validate auth configuration
        if config.api.enable_auth and not (config.api.api_key or config.api.jwt_secret):
            raise ConfigError("API authentication enabled but no API key or JWT secret provided")
        
        # Validate database path
        db_dir = os.path.dirname(config.database.path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except OSError as e:
                raise ConfigError(f"Cannot create database directory {db_dir}: {e}")


class ConfigLoader:
    """Configuration loader with environment variable support"""
    
    ENV_PREFIX = "NEASMART_"
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ConfigError(f"Error loading configuration file: {e}")
    
    @classmethod
    def load_from_env(cls) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {}
        
        # Map of environment variables to config paths
        env_mapping = {
            "DATABASE_PATH": "database.path",
            "DATABASE_ENABLE_FALLBACK": "database.enable_fallback",
            "MODBUS_SLAVE_ID": "modbus.slave_id",
            "MODBUS_SYNC_ON_STARTUP": "modbus.sync_on_startup",
            "GATEWAY_SERVER_TYPE": "server.type",
            "GATEWAY_SERVER_ADDRESS": "server.address",
            "GATEWAY_SERVER_PORT": "server.port",
            "GATEWAY_SERVER_SERIAL_PORT": "server.serial_port",
            "API_HOST": "api.host",
            "API_PORT": "api.port",
            "API_ENABLE_AUTH": "api.enable_auth",
            "API_KEY": "api.api_key",
            "API_JWT_SECRET": "api.jwt_secret",
            "API_TEMPERATURE_UNIT": "api.temperature_unit",
            "LOG_LEVEL": "logging.level",
            "LOG_FILE": "logging.file_path",
            "DEBUG_MODE": "debug_mode",
        }
        
        for env_key, config_path in env_mapping.items():
            env_var = f"{cls.ENV_PREFIX}{env_key}"
            value = os.environ.get(env_var)
            
            if value is not None:
                # Convert value to appropriate type
                if value.lower() in ["true", "false"]:
                    value = value.lower() == "true"
                elif value.isdigit():
                    value = int(value)
                elif env_key in ["RETRY_BASE_DELAY", "RETRY_MAX_DELAY"]:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                
                # Set nested config value
                cls._set_nested_value(config, config_path, value)
                logger.info(f"Loaded {config_path} from environment: {env_var}")
        
        return config
    
    @staticmethod
    def _set_nested_value(config: Dict[str, Any], path: str, value: Any) -> None:
        """Set a nested dictionary value using dot notation"""
        keys = path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    @classmethod
    def merge_configs(cls, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries"""
        result = {}
        
        for config in configs:
            cls._deep_merge(result, config)
        
        return result
    
    @staticmethod
    def _deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Deep merge source dictionary into target"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                ConfigLoader._deep_merge(target[key], value)
            else:
                target[key] = value
    
    @classmethod
    def create_config(cls, config_dict: Dict[str, Any]) -> AppConfig:
        """Create AppConfig instance from dictionary"""
        # Create nested dataclass instances
        database_config = DatabaseConfig(**config_dict.get('database', {}))
        modbus_config = ModbusConfig(**config_dict.get('modbus', {}))
        
        # Handle server type enum
        server_dict = config_dict.get('server', {})
        if 'type' in server_dict:
            server_dict['type'] = ServerType(server_dict['type'])
        server_config = ServerConfig(**server_dict)
        
        api_config = APIConfig(**config_dict.get('api', {}))
        logging_config = LoggingConfig(**config_dict.get('logging', {}))
        
        # Create main config
        app_config = AppConfig(
            database=database_config,
            modbus=modbus_config,
            server=server_config,
            api=api_config,
            logging=logging_config,
            **{k: v for k, v in config_dict.items() 
               if k not in ['database', 'modbus', 'server', 'api', 'logging']}
        )
        
        return app_config


def load_config(config_file: Optional[str] = None) -> AppConfig:
    """
    Load configuration from file and environment variables.
    Environment variables take precedence over file configuration.
    """
    # Define project root (assuming config.py is in src/)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Start with default configuration
    config_dict = {}
    
    # Default config file path relative to project root
    if config_file is None:
        config_file = os.environ.get(
            f"{ConfigLoader.ENV_PREFIX}CONFIG_FILE",
            os.path.join(project_root, "data", "config.json")
        )

    # Load from file if provided
    if os.path.exists(config_file):
        file_config = ConfigLoader.load_from_file(config_file)
        config_dict = ConfigLoader.merge_configs(config_dict, file_config)
        logger.info(f"Loaded configuration from file: {config_file}")
    
    # Load from environment variables (overrides file config)
    env_config = ConfigLoader.load_from_env()
    config_dict = ConfigLoader.merge_configs(config_dict, env_config)
    
    # Create config object
    config = ConfigLoader.create_config(config_dict)

    # Resolve paths to be absolute, relative to project root
    if not os.path.isabs(config.database.path):
        config.database.path = os.path.join(project_root, config.database.path)
    
    if config.logging.file_path and not os.path.isabs(config.logging.file_path):
        config.logging.file_path = os.path.join(project_root, config.logging.file_path)

    # Validate configuration
    ConfigValidator.validate_config(config)
    
    return config


def save_config(config: AppConfig, file_path: str) -> None:
    """Save configuration to file"""
    try:
        # Convert to dictionary
        config_dict = asdict(config)
        
        # Convert enums to strings
        if 'server' in config_dict and 'type' in config_dict['server']:
            config_dict['server']['type'] = config_dict['server']['type'].value
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Configuration saved to: {file_path}")
        
    except Exception as e:
        raise ConfigError(f"Failed to save configuration: {e}")


# Singleton config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get current configuration instance"""
    global _config
    
    if _config is None:
        # load_config will use default if env var is not set
        config_file = os.environ.get(f"{ConfigLoader.ENV_PREFIX}CONFIG_FILE")
        _config = load_config(config_file)
    
    return _config


def set_config(config: AppConfig) -> None:
    """Set configuration instance"""
    global _config
    ConfigValidator.validate_config(config)
    _config = config 