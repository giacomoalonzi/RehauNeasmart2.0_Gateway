#!/usr/bin/env python3

"""
Gateway Control Script

This script allows you to enable/disable the Waveshare gateway write-through
and check the current status.
"""

import json
import os
import sys
import argparse


def load_config():
    """Load gateway configuration."""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'gateway.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}")
        return None


def save_config(config):
    """Save gateway configuration."""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'gateway.json')
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def show_status():
    """Show current gateway status."""
    config = load_config()
    if not config:
        return
    
    gateway_config = config.get('gateway', {})
    fallback_config = config.get('fallback', {})
    
    print("=== Gateway Status ===")
    print(f"Enabled: {gateway_config.get('enabled', True)}")
    print(f"Host: {gateway_config.get('host', '0.0.0.0')}")
    print(f"Port: {gateway_config.get('port', 502)}")
    print(f"Neasmart Slave ID: {gateway_config.get('neasmart_slave_id', 240)}")
    print(f"Timeout: {gateway_config.get('timeout', 5)}s")
    print(f"Retry Attempts: {gateway_config.get('retry_attempts', 3)}")
    print(f"Retry Delay: {gateway_config.get('retry_delay', 1)}s")
    print()
    print("=== Fallback Settings ===")
    print(f"Disable on Error: {fallback_config.get('disable_write_through_on_error', False)}")
    print(f"Max Consecutive Errors: {fallback_config.get('max_consecutive_errors', 3)}")
    print(f"Error Reset Interval: {fallback_config.get('error_reset_interval', 300)}s")


def enable_gateway():
    """Enable gateway write-through."""
    config = load_config()
    if not config:
        return False
    
    config['gateway']['enabled'] = True
    if save_config(config):
        print("✅ Gateway write-through enabled")
        return True
    return False


def disable_gateway():
    """Disable gateway write-through."""
    config = load_config()
    if not config:
        return False
    
    config['gateway']['enabled'] = False
    if save_config(config):
        print("❌ Gateway write-through disabled")
        return True
    return False


def enable_fallback():
    """Enable automatic fallback on errors."""
    config = load_config()
    if not config:
        return False
    
    config['fallback']['disable_write_through_on_error'] = True
    if save_config(config):
        print("🔄 Automatic fallback enabled - gateway will be disabled after consecutive errors")
        return True
    return False


def disable_fallback():
    """Disable automatic fallback on errors."""
    config = load_config()
    if not config:
        return False
    
    config['fallback']['disable_write_through_on_error'] = False
    if save_config(config):
        print("🔄 Automatic fallback disabled - gateway will continue trying despite errors")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description='Control Waveshare gateway write-through')
    parser.add_argument('action', choices=['status', 'enable', 'disable', 'enable-fallback', 'disable-fallback'],
                       help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'status':
        show_status()
    elif args.action == 'enable':
        enable_gateway()
    elif args.action == 'disable':
        disable_gateway()
    elif args.action == 'enable-fallback':
        enable_fallback()
    elif args.action == 'disable-fallback':
        disable_fallback()


if __name__ == '__main__':
    main()
