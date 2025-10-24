#!/usr/bin/env python3

import json
import logging
import os
from dataclasses import dataclass
from typing import Union

_logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Configuration class for server settings."""
    
    listen_address: str = "0.0.0.0"
    listen_port: int = 502
    server_type: str = "tcp"
    slave_id: int = 240
    server_port: int = 5001
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.server_type not in ["tcp", "serial"]:
            raise ValueError(f"Invalid server_type: {self.server_type}")
        if self.slave_id < 1 or self.slave_id > 255:
            raise ValueError(f"Invalid slave_id: {self.slave_id}")
        if self.listen_port < 1 or self.listen_port > 65535:
            raise ValueError(f"Invalid listen_port: {self.listen_port}")


class ConfigManager:
    """Configuration manager for loading and managing application settings."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config_path = config_path or "./data/options.json"
        self._config = None
    
    def load_config(self) -> ServerConfig:
        """
        Load configuration from JSON file.
        
        Returns:
            ServerConfig: Loaded configuration object
        """
        if not os.path.exists(self.config_path):
            _logger.warning(f"Configuration file not found at {self.config_path}, using defaults")
            return ServerConfig()
        
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            # Convert string values to appropriate types
            config_data['listen_port'] = int(config_data.get('listen_port', 502))
            config_data['slave_id'] = int(config_data.get('slave_id', 240))
            config_data['server_port'] = int(config_data.get('server_port', 5001))
            
            self._config = ServerConfig(**config_data)
            _logger.info(f"Configuration loaded from {self.config_path}")
            return self._config
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
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
    
    def save_config(self, config: ServerConfig) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            config (ServerConfig): Configuration to save
        """
        try:
            config_dict = {
                'listen_address': config.listen_address,
                'listen_port': str(config.listen_port),
                'server_type': config.server_type,
                'slave_id': str(config.slave_id),
                'server_port': str(config.server_port)
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            _logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            _logger.error(f"Error saving configuration: {e}")
            raise


# Global configuration manager instance
config_manager = ConfigManager()
