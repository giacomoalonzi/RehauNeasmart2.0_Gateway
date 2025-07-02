# Configuration Guide

This guide explains all configuration options for the Rehau Neasmart 2.0 Gateway.

## Configuration File

The gateway uses a JSON configuration file located at `data/config.json`. You can copy from the example below and modify as needed.

## Example Configuration

```json
{
  "server": {
    "type": "tcp",
    "address": "192.168.1.100",
    "port": 502
  },
  "modbus": {
    "slave_id": 240,
    "sync_on_startup": true,
    "circuit_breaker_failure_threshold": 5,
    "circuit_breaker_recovery_timeout": 60
  },
  "api": {
    "host": "0.0.0.0",
    "port": 5001,
    "enable_auth": false,
    "api_key": "your-secret-key",
    "rate_limit_per_minute": 60,
    "enable_cors": true,
    "cors_origins": ["*"]
  },
  "database": {
    "path": "./data/registers.db",
    "enable_fallback": true,
    "retry_max_attempts": 3,
    "table_name": "registers"
  },
  "logging": {
    "level": "INFO",
    "enable_file": true,
    "file_path": "./data/gateway.log",
    "enable_console": true,
    "max_file_size_mb": 10,
    "backup_count": 5,
    "format": "text"
  },
  "debug_mode": false
}
```

## Configuration Options

### Server Section

- **type**: Connection type. Options: `"tcp"` or `"serial"`
- **address**: IP address of the Modbus device (for TCP) or `"0.0.0.0"` to listen on all interfaces
- **port**: Port number (default: 502). Use 5502 if 502 is already in use

For serial connections, add:

- **serial_port**: Serial port path (e.g., `"/dev/ttyUSB0"`)
- **serial_baudrate**: Baud rate (default: 38400)
- **serial_parity**: Parity (default: "N")
- **serial_stopbits**: Stop bits (default: 1)
- **serial_bytesize**: Byte size (default: 8)

### Modbus Section

- **slave_id**: Modbus slave ID (default: 240)
- **sync_on_startup**: Sync all values from bus on startup (default: false)
- **circuit_breaker_failure_threshold**: Failures before circuit opens (default: 5)
- **circuit_breaker_recovery_timeout**: Seconds before retry (default: 60)

### API Section

- **host**: API bind address (default: "0.0.0.0")
- **port**: API port (default: 5001). Use 5501 if 5001 is already in use
- **enable_auth**: Enable API authentication (default: false, set to true for production)
- **api_key**: API key for authentication (required if enable_auth is true)
- **rate_limit_per_minute**: Max requests per minute per IP (default: 60)
- **enable_cors**: Enable CORS support (default: true)
- **cors_origins**: Allowed CORS origins (default: ["*"], restrict in production)

### Database Section

- **path**: Database file path (default: "./data/registers.db")
- **enable_fallback**: Use in-memory storage if database fails (default: true)
- **retry_max_attempts**: Max retry attempts for database operations (default: 3)
- **table_name**: Database table name (default: "registers")

### Logging Section

- **level**: Log level. Options: "DEBUG", "INFO", "WARNING", "ERROR" (default: "INFO")
- **enable_file**: Enable file logging (default: true)
- **file_path**: Log file path (default: "./data/gateway.log")
- **enable_console**: Enable console logging (default: true)
- **max_file_size_mb**: Max log file size before rotation (default: 10)
- **backup_count**: Number of rotated log files to keep (default: 5)
- **format**: Log format. Options: "text" or "json" (default: "text")

### Other Options

- **debug_mode**: Enable debug mode (default: false, set to true for development)

## Environment Variables

All configuration options can be overridden using environment variables:

```bash
# Examples
export NEASMART_SERVER_TYPE=tcp
export NEASMART_SERVER_ADDRESS=192.168.1.100
export NEASMART_SERVER_PORT=502
export NEASMART_MODBUS_SLAVE_ID=240
export NEASMART_API_PORT=5001
export NEASMART_API_ENABLE_AUTH=true
export NEASMART_API_KEY=your-secret-key
export NEASMART_LOG_LEVEL=DEBUG
```

Environment variables take precedence over the configuration file.
