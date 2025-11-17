# Rehau Neasmart 2.0 Gateway

> **Disclaimer**: This is a Docker-based port of the [original project](https://github.com/MatteoManzoni/RehauNeasmart2.0_Gateway), designed for integration with Home Assistant. It acts as a bridge between the Rehau Neasmart 2.0 SysBus (Modbus variant) and Home Assistant, exposing it as a climate entity.

## Overview

The Rehau Neasmart 2.0 Gateway provides a REST API gateway to integrate **Rehau Neasmart 2.0** heating systems with **Home Assistant** and other automation platforms. It supports both Modbus TCP and Modbus Serial (RS485) connections, with SQLite-based persistent register storage.

### Key Features

- **REST API** with OpenAPI/Swagger documentation
- **Modbus TCP and Serial (RS485)** support
- **SQLite-based persistent storage** for register data
- **JSON-based configuration** system
- **Dockerized** for easy deployment
- **Human-readable state values** (e.g., "presence", "auto" instead of integers)

---

## Quick Start

### Prerequisites

- Docker installed on your system
- Access to the Rehau Neasmart 2.0 SysBus interface
- RS485-to-TCP adapter (e.g., Waveshare RS485 PoE Gateway)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/RehauNeasmart2.0_Gateway.git
   cd RehauNeasmart2.0_Gateway
   ```

2. **Configure the gateway** (see [Configuration](#configuration) section below)

3. **Build and run with Docker**:
   ```bash
   docker build -t rehauneasmart-gateway .
   docker run -d \
       --name rehauneasmart-gateway \
       -p 5001:5001 \
       -p 502:502 \
       -v $(pwd)/config:/app/config \
       -v $(pwd)/data:/app/data \
       rehauneasmart-gateway
   ```

4. **Verify the installation**:
   ```bash
   curl http://localhost:5001/api/health
   ```

---

## Configuration

The gateway uses a JSON-based configuration system located in the `config/` directory. All configuration files are modular and can be customized for your specific setup.

### Configuration Setup

1. **Copy example configuration file**:
   ```bash
   cp config/example/config.json.example config/config.json
   ```

2. **Edit `config/config.json`** according to your setup (see details below)

3. **Mount the config directory** when running Docker (as shown in the installation steps)

### Configuration File

All application settings are consolidated in a single `config.json` file located in the `config/` directory. This unified configuration replaces the previous multi-file structure for easier management.

#### `config.json`

The unified configuration file contains all application settings organized into logical sections:

```json
{
  "// SERVER & MODBUS CONFIGURATION": "",
  "server": {
    "type": "tcp",                    // "tcp" or "serial"
    "address": "0.0.0.0",             // TCP bind address
    "port": 502,                       // Modbus TCP port
    "server_port": 5001,               // REST API port
    "serial_port": "/dev/ttyUSB0",     // Serial port (if type="serial")
    "serial_baudrate": 38400           // Serial baudrate (if type="serial")
  },
  "modbus": {
    "slave_id": 240,                   // Modbus slave ID of your Neasmart system
    "sync_on_startup": false,
    "sync_batch_size": 100,
    "circuit_breaker_failure_threshold": 5,
    "circuit_breaker_recovery_timeout": 60,
    "circuit_breaker_half_open_calls": 3
  },
  "// API SERVER CONFIGURATION": "",
  "api": {
    "host": "0.0.0.0",
    "port": 5001,
    "enable_auth": false,
    "rate_limit_per_minute": 60,
    "enable_cors": true,
    "cors_origins": ["*"],
    "request_timeout": 30,
    "max_request_size": 1048576,
    "temperature_unit": "C"
  },
  "// GATEWAY CONFIGURATION": "",
  "gateway": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 502,
    "neasmart_slave_id": 240,
    "timeout": 15,
    "retry_attempts": 3,
    "retry_delay": 3
  },
  "// FALLBACK CONFIGURATION": "",
  "fallback": {
    "disable_write_through_on_error": true,
    "max_consecutive_errors": 3,
    "error_reset_interval": 300
  },
  "// ZONES CONFIGURATION": "",
  "zones": {
    "structures": [
      {
        "base_id": 1,
        "base_label": "First Floor",
        "zones": [
          { "id": 1, "label": "Living Room" },
          { "id": 2, "label": "Kitchen" },
          { "id": 3, "label": "Bedroom" }
        ]
      }
    ]
  },
  "// DATABASE CONFIGURATION": "",
  "database": {
    "path": "./data/registers.db",
    "table_name": "holding_registers",
    "enable_fallback": true,
    "retry_max_attempts": 3,
    "retry_base_delay": 0.1,
    "retry_max_delay": 1.0,
    "health_check_interval": 30
  },
  "// LOGGING CONFIGURATION": "",
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": "./data/gateway.log",
    "max_file_size": 10485760,
    "backup_count": 5,
    "enable_console": true,
    "enable_file": true
  },
  "// FEATURE FLAGS": "",
  "features": {
    "enable_health_endpoint": true,
    "enable_metrics": true,
    "enable_swagger": true,
    "debug_mode": false
  },
  "// ADVANCED SETTINGS": "",
  "advanced": {
    "circuit_breaker_enabled": true,
    "auto_discovery": false,
    "performance_monitoring": true,
    "cache_enabled": true,
    "cache_ttl": 300
  }
}
```

**Key Configuration Sections**:

- **`server`** - Server and Modbus connection settings (required)
  - `type`: Connection type - `"tcp"` or `"serial"`
  - `address`: TCP bind address (for TCP mode)
  - `port`: Modbus TCP port (default: 502)
  - `server_port`: REST API port (default: 5001)
  - Serial settings (`serial_port`, `serial_baudrate`, etc.) for serial mode

- **`modbus`** - Modbus protocol settings
  - `slave_id`: Modbus slave ID of your Neasmart system (required)

- **`api`** - REST API server configuration
  - `host`: API server bind address
  - `port`: API server port
  - `enable_cors`: Enable CORS support
  - `temperature_unit`: Temperature unit (`"C"` or `"F"`)

- **`gateway`** - Waveshare gateway connection settings
  - `enabled`: Enable/disable gateway write-through
  - `host`: Gateway IP address
  - `port`: Gateway port
  - `neasmart_slave_id`: Neasmart device slave ID

- **`fallback`** - Error handling and fallback behavior
  - `disable_write_through_on_error`: Auto-disable gateway on errors
  - `max_consecutive_errors`: Max errors before disabling
  - `error_reset_interval`: Error reset interval in seconds

- **`zones`** - Building structure and zone definitions (required)
  - `structures`: Array of building structures with zones
  - **Important**: The `base_id` and zone `id` values must match your physical Neasmart system configuration

- **`database`** - Database persistence settings
  - `path`: SQLite database file path
  - `enable_fallback`: Enable database fallback mode

- **`logging`** - Logging configuration
  - `level`: Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
  - `file_path`: Log file path
  - `enable_console`: Enable console logging
  - `enable_file`: Enable file logging

- **`features`** - Feature flags
  - `enable_health_endpoint`: Enable `/api/health` endpoint
  - `enable_swagger`: Enable Swagger UI documentation
  - `debug_mode`: Enable debug mode

- **`advanced`** - Advanced settings
  - `circuit_breaker_enabled`: Enable circuit breaker pattern
  - `cache_enabled`: Enable response caching
  - `cache_ttl`: Cache time-to-live in seconds

**Common configurations**:
- **Modbus TCP**: Set `server.type: "tcp"` and configure `server.address` and `server.port`
- **Modbus Serial**: Set `server.type: "serial"` and configure `server.serial_port` and `server.serial_baudrate`

### Environment Variables

You can override configuration values using environment variables with the format:
- `NEASMART_<SECTION>_<KEY>` (e.g., `NEASMART_SERVER_TYPE=tcp`)
- `NEASMART_API_PORT=5001`
- `NEASMART_DATABASE_PATH=./data/registers.db`

### Configuration Examples

See `config/example/config.json.example` for a complete example configuration with detailed comments.

---

## REST API

The gateway exposes a REST API under the `/api` prefix. Interactive API documentation is available at `/api/docs` (Swagger UI) when enabled in `config.json` (`features.enable_swagger`).

### Base URL

- **Local**: `http://localhost:5001/api`
- **Docker**: `http://<container-ip>:5001/api`

### Endpoints

#### Health Check
- **GET** `/api/health` - Check gateway health status

**Response**:
```json
{
  "version": "2.0.0",
  "healthy": true
}
```

#### Zones
- **GET** `/api/zones` - List all configured zones
- **GET** `/api/zones/<base_id>/<zone_id>` - Get zone information (state, temperature, setpoint, humidity)
- **POST** `/api/zones/<base_id>/<zone_id>` - Update zone state or setpoint

**Example**:
```bash
# Get zone data
curl http://localhost:5001/api/zones/1/1

# Set zone setpoint
curl -X POST http://localhost:5001/api/zones/1/1 \
  -H "Content-Type: application/json" \
  -d '{"setpoint": 22.5}'
```

#### Operation Mode & State
- **GET** `/api/mode` - Get current operation mode
- **POST** `/api/mode` - Set operation mode
- **GET** `/api/state` - Get current operation state
- **POST** `/api/state` - Set operation state

**Example**:
```bash
# Get operation mode
curl http://localhost:5001/api/mode

# Set operation state
curl -X POST http://localhost:5001/api/state \
  -H "Content-Type: application/json" \
  -d '{"state": "presence"}'
```

#### Temperature
- **GET** `/api/outsidetemperature` - Get outside temperature data

#### Devices
- **GET** `/api/dehumidifiers/<id>` - Get dehumidifier status
- **GET** `/api/pumps/<id>` - Get pump status
- **GET** `/api/mixedgroups/<group_id>` - Get mixed group data

#### Notifications
- **GET** `/api/notifications` - Get system notifications (hints, warnings, errors)

### API Response Format

All API responses use **camelCase** field naming (e.g., `relativeHumidity`, `outsideTemperature`). State and mode values are returned as human-readable strings (e.g., `"presence"`, `"auto"`) instead of integers.

**Example zone response**:
```json
{
  "state": "presence",
  "setpoint": 21.5,
  "temperature": 22.0,
  "relativeHumidity": 45
}
```

For complete API documentation, visit `/api/docs` or see `API_DOCS.md`.

---

## Docker Deployment

### Basic Docker Run

```bash
docker run -d \
  --name rehauneasmart-gateway \
  -p 5001:5001 \
  -p 502:502 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  rehauneasmart-gateway
```

### Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  gateway:
    build: .
    container_name: rehauneasmart-gateway
    ports:
      - "5001:5001"
      - "502:502"
    volumes:
      - ./config:/app/config
      - ./data:/app/data
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

---

## Troubleshooting

### Check Logs
```bash
docker logs rehauneasmart-gateway
# or
tail -f data/gateway.log
```

### Verify Configuration
The gateway validates all configuration files on startup. Check logs for configuration errors.

### Database Issues
- Ensure the `data/` directory exists and is writable
- Database file: `data/registers.db`
- Check database permissions if running in Docker

### Connection Issues
- **Modbus TCP**: Verify network connectivity and firewall settings
- **Modbus Serial**: Check serial port permissions (`/dev/ttyUSB0` access)
- Verify Modbus slave ID matches your Neasmart system

### API Not Accessible
- Check API port (default: 5001) is not blocked by firewall
- Verify `config.json` API configuration (`api` section)
- Check container logs for binding errors

---

## Development

### Running Locally (without Docker)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure**: Copy and edit configuration files in `config/`

3. **Run**:
   ```bash
   python3 src/main.py
   ```

### Running Tests

```bash
cd src
python -m unittest test_dpt_9001
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Commit your changes
4. Submit a pull request

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## Support

For questions or issues, open an issue on [GitHub](https://github.com/your-username/RehauNeasmart2.0_Gateway/issues).
