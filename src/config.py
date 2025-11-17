#!/usr/bin/env python3

import json
import logging
import os
from dataclasses import dataclass
from typing import Union, Dict, Any, List

_logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Configuration class for server settings."""
    
    listen_address: str = "0.0.0.0"
    listen_port: int = 502
    server_type: str = "tcp"
    slave_id: int = 240
    server_port: int = 5001
    structures: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.server_type not in ["tcp", "serial"]:
            raise ValueError(f"Invalid server_type: {self.server_type}")
        if self.slave_id < 1 or self.slave_id > 255:
            raise ValueError(f"Invalid slave_id: {self.slave_id}")
        if self.listen_port < 1 or self.listen_port > 65535:
            raise ValueError(f"Invalid listen_port: {self.listen_port}")
        if self.structures is None:
            self.structures = []


class ConfigManager:
    """Configuration manager for loading and managing application settings from unified config.json."""
    
    def __init__(self, config_dir: str = "./config"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir (str): Path to configuration directory
        """
        self.config_dir = config_dir
        self._config = None
        self._full_config = None
    
    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Load and parse a JSON configuration file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            _logger.warning(f"Error loading {file_path}: {e}")
            return {}
    
    def load_config(self) -> ServerConfig:
        """
        Load configuration from unified config.json file.
        
        Returns:
            ServerConfig: Loaded configuration object
        """
        try:
            # Load unified configuration
            config_path = os.path.join(self.config_dir, "config.json")
            self._full_config = self._load_json_file(config_path)
            
            # Extract server settings
            server_info = self._full_config.get('server', {})
            modbus_info = self._full_config.get('modbus', {})
            zones_info = self._full_config.get('zones', {})
            
            # Build configuration data
            config_data = {
                'listen_address': server_info.get('address', '0.0.0.0'),
                'listen_port': server_info.get('port', 502),
                'server_type': server_info.get('type', 'tcp'),
                'slave_id': modbus_info.get('slave_id', 240),
                'server_port': server_info.get('server_port', 5001),
                'structures': zones_info.get('structures', [])
            }
            
            self._config = ServerConfig(**config_data)
            _logger.info(f"Configuration loaded from {config_path}")
            return self._config
            
        except Exception as e:
            _logger.error(f"Error loading configuration: {e}")
            _logger.info("Using default configuration")
            self._full_config = {}
            return ServerConfig()
    
    def get_config(self) -> ServerConfig:
        """
        Get current configuration, loading if necessary.
        
        Returns:
            ServerConfig: Current configuration
        """
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def get_zones_config(self) -> Dict[str, Any]:
        """
        Get zones configuration.
        
        Returns:
            Dict[str, Any]: Zones configuration
        """
        if self._full_config is None:
            self.load_config()
        return self._full_config.get('zones', {})
    
    def get_gateway_config(self) -> Dict[str, Any]:
        """
        Get gateway configuration.
        
        Returns:
            Dict[str, Any]: Gateway configuration
        """
        if self._full_config is None:
            self.load_config()
        return self._full_config.get('gateway', {})
    
    def get_fallback_config(self) -> Dict[str, Any]:
        """
        Get fallback configuration.
        
        Returns:
            Dict[str, Any]: Fallback configuration
        """
        if self._full_config is None:
            self.load_config()
        return self._full_config.get('fallback', {})
    
    def get_full_config(self) -> Dict[str, Any]:
        """
        Get the full configuration dictionary.
        
        Returns:
            Dict[str, Any]: Full configuration
        """
        if self._full_config is None:
            self.load_config()
        return self._full_config.copy() if self._full_config else {}
    
    def save_config(self, config: ServerConfig) -> None:
        """
        Save configuration to unified config.json file.
        
        Args:
            config (ServerConfig): Configuration to save
        """
        try:
            # Load current full config
            config_path = os.path.join(self.config_dir, "config.json")
            full_config = self.get_full_config()
            
            # Update server settings
            if 'server' not in full_config:
                full_config['server'] = {}
            
            full_config['server'].update({
                'address': config.listen_address,
                'port': config.listen_port,
                'type': config.server_type,
                'server_port': config.server_port
            })
            
            # Update modbus settings
            if 'modbus' not in full_config:
                full_config['modbus'] = {}
            
            full_config['modbus']['slave_id'] = config.slave_id
            
            # Update zones settings
            if 'zones' not in full_config:
                full_config['zones'] = {}
            
            full_config['zones']['structures'] = config.structures
            
            # Save unified configuration
            with open(config_path, 'w') as f:
                json.dump(full_config, f, indent=2)
            
            # Reload to refresh internal state
            self._full_config = full_config
            _logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            _logger.error(f"Error saving configuration: {e}")
            raise
    
    def save_full_config(self, full_config: Dict[str, Any]) -> None:
        """
        Save the full configuration dictionary.
        
        Args:
            full_config (Dict[str, Any]): Full configuration to save
        """
        try:
            config_path = os.path.join(self.config_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(full_config, f, indent=2)
            
            # Reload to refresh internal state
            self._full_config = full_config
            self._config = None  # Force reload of ServerConfig
            _logger.info(f"Full configuration saved to {config_path}")
            
        except Exception as e:
            _logger.error(f"Error saving full configuration: {e}")
            raise


# Global configuration manager instance
config_manager = ConfigManager()
