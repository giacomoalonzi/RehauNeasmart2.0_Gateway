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
    """Configuration manager for loading and managing application settings from config/ directory."""
    
    def __init__(self, config_dir: str = "./config"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir (str): Path to configuration directory
        """
        self.config_dir = config_dir
        self._config = None
        self._zones_config = None
    
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
        Load configuration from config/ directory.
        
        Returns:
            ServerConfig: Loaded configuration object
        """
        try:
            # Load server configuration
            server_config_path = os.path.join(self.config_dir, "server.json")
            server_data = self._load_json_file(server_config_path)
            
            # Load zones configuration
            zones_config_path = os.path.join(self.config_dir, "zones.json")
            zones_data = self._load_json_file(zones_config_path)
            
            # Extract server settings
            server_info = server_data.get('server', {})
            modbus_info = server_data.get('modbus', {})
            
            # Build configuration data
            config_data = {
                'listen_address': server_info.get('address', '0.0.0.0'),
                'listen_port': server_info.get('port', 502),
                'server_type': server_info.get('type', 'tcp'),
                'slave_id': modbus_info.get('slave_id', 240),
                'server_port': server_info.get('server_port', 5001),
                'structures': zones_data.get('structures', [])
            }
            
            self._config = ServerConfig(**config_data)
            self._zones_config = zones_data
            _logger.info(f"Configuration loaded from {self.config_dir}")
            return self._config
            
        except Exception as e:
            _logger.error(f"Error loading configuration: {e}")
            _logger.info("Using default configuration")
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
        if self._zones_config is None:
            self.load_config()
        return self._zones_config or {}
    
    def save_config(self, config: ServerConfig) -> None:
        """
        Save configuration to config/ directory.
        
        Args:
            config (ServerConfig): Configuration to save
        """
        try:
            # Save server configuration
            server_config_path = os.path.join(self.config_dir, "server.json")
            server_data = self._load_json_file(server_config_path)
            
            # Update server settings
            if 'server' not in server_data:
                server_data['server'] = {}
            
            server_data['server'].update({
                'address': config.listen_address,
                'port': config.listen_port,
                'type': config.server_type,
                'server_port': config.server_port
            })
            
            if 'modbus' not in server_data:
                server_data['modbus'] = {}
            
            server_data['modbus']['slave_id'] = config.slave_id
            
            with open(server_config_path, 'w') as f:
                json.dump(server_data, f, indent=2)
            
            # Save zones configuration
            zones_config_path = os.path.join(self.config_dir, "zones.json")
            zones_data = {
                'structures': config.structures
            }
            
            with open(zones_config_path, 'w') as f:
                json.dump(zones_data, f, indent=2)
            
            _logger.info(f"Configuration saved to {self.config_dir}")
            
        except Exception as e:
            _logger.error(f"Error saving configuration: {e}")
            raise


# Global configuration manager instance
config_manager = ConfigManager()
