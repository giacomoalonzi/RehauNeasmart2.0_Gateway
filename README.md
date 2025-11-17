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
  "// SERVER CONFIGURATION": "",
  "server": {
    "type": "tcp",                    // "tcp" or "serial"
    "address": "0.0.0.0",             // TCP bind address (for TCP mode)
    "port": 502,                       // Modbus TCP port (default: 502)
    "server_port": 5001                // REST API port (default: 5001)
  },
  "// MODBUS CONFIGURATION": "",
  "modbus": {
    "slave_id": 240                    // Modbus slave ID of your Neasmart system (1-255, required)
  },
  "// GATEWAY CONFIGURATION": "",
  "gateway": {
    "enabled": true,                   // Enable/disable gateway write-through
    "host": "127.0.0.1",               // Waveshare gateway IP address
    "port": 502,                       // Waveshare gateway port
    "neasmart_slave_id": 240,          // Neasmart device slave ID
    "timeout": 15,                     // Connection timeout in seconds
    "retry_attempts": 3,               // Number of retry attempts on failure
    "retry_delay": 3                   // Delay between retries in seconds
  },
  "// FALLBACK CONFIGURATION": "",
  "fallback": {
    "disable_write_through_on_error": true,  // Automatically disable write-through on consecutive errors
    "max_consecutive_errors": 3,              // Maximum consecutive errors before disabling
    "error_reset_interval": 300              // Error reset interval in seconds
  },
  "// ZONES CONFIGURATION": "",
  "zones": {
    "structures": [
      {
        "base_id": 1,                  // Base ID (1-4) - must match your Neasmart system
        "base_label": "First Floor",    // Human-readable label for this structure
        "zones": [
          { "id": 1, "label": "Living Room" },
          { "id": 2, "label": "Kitchen" },
          { "id": 3, "label": "Bedroom" }
        ]
      }
    ]
  }
}
```

**Configuration Sections**:

- **`server`** - Modbus server and REST API settings (required)
  - `type`: Connection type - `"tcp"` for Modbus TCP or `"serial"` for Modbus RTU over serial
  - `address`: TCP bind address (for TCP mode, default: `"0.0.0.0"`)
  - `port`: Modbus TCP port (default: `502`)
  - `server_port`: REST API server port (default: `5001`)
  - **Note**: Serial port settings (baudrate, parity, etc.) are hardcoded in the application according to Neasmart specifications

- **`modbus`** - Modbus protocol settings (required)
  - `slave_id`: Modbus slave ID of your Neasmart system (1-255, default: `240`)

- **`gateway`** - Waveshare gateway connection settings
  - `enabled`: Enable/disable gateway write-through (default: `true`)
  - `host`: Waveshare gateway IP address - **This is different from `server.address`**:
    - `server.address` is where **our Modbus server listens** (receives connections)
    - `gateway.host` is where **our Modbus client connects** to the Waveshare hardware gateway
    - Use `"127.0.0.1"` if the gateway is on the same machine, or the gateway's actual IP if on a different machine (default: `"127.0.0.1"`)
  - `port`: Waveshare gateway port (default: `502`)
  - `neasmart_slave_id`: Neasmart device slave ID (default: `240`)
  - `timeout`: Connection timeout in seconds (default: `15`)
  - `retry_attempts`: Number of retry attempts on failure (default: `3`)
  - `retry_delay`: Delay between retries in seconds (default: `3`)

- **`fallback`** - Error handling and fallback behavior
  - `disable_write_through_on_error`: Automatically disable gateway write-through on consecutive errors (default: `true`)
  - `max_consecutive_errors`: Maximum consecutive errors before disabling (default: `3`)
  - `error_reset_interval`: Error reset interval in seconds (default: `300`)

- **`zones`** - Building structure and zone definitions (required)
  - `structures`: Array of building structures with zones
  - Each structure contains:
    - `base_id`: Base ID (1-4) - must match your physical Neasmart system configuration
    - `base_label`: Human-readable label for the structure
    - `zones`: Array of zone objects with `id` and `label`
  - **Important**: The `base_id` and zone `id` values must match your physical Neasmart system configuration

**Common configurations**:
- **Modbus TCP**: Set `server.type: "tcp"` and configure `server.address` and `server.port`
- **Modbus Serial**: Set `server.type: "serial"` (serial port settings are automatically configured according to Neasmart specifications)

### Environment Variables

You can override configuration values using environment variables with the format:
- `NEASMART_<SECTION>_<KEY>` (e.g., `NEASMART_SERVER_TYPE=tcp`)
- `NEASMART_SERVER_PORT=5001`

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

All API responses use **camelCase** field naming (e.g., `relativeHumidity`, `outsideTemperature`). State and mode values are returned as human-readable strings (e.g., `"presence"`, `"auto"`) instead of integers. **API requests must also use human-readable strings for state and mode values** - integer values are not accepted.

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
