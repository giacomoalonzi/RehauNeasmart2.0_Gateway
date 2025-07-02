# Rehau Neasmart 2.0 Gateway

[![Docker](https://img.shields.io/badge/docker-supported-blue)](https://www.docker.com/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern Python gateway for interfacing with Rehau Neasmart 2.0 heating/cooling systems via Modbus protocol. Features a RESTful API, automatic data persistence, and comprehensive monitoring capabilities.

## Quick Start

### Development Mode (Python venv)

```bash
# Setup
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Configure
cp data/config.json.example data/config.json
# Edit data/config.json with your Modbus settings and zone structure

# Run
python src/main.py
# API available at http://localhost:5001
```

### Production Mode (Docker)

```bash
# Configure
cp data/config.json.example data/config.json
cp env.example .env
# Edit config.json and .env files

# Run
docker-compose up -d
# API available at http://localhost:5000
```

## Configuration

The gateway supports **flexible configuration options**:

### 🆕 Modular Configuration (Recommended)

Separate files for better organization:

```
config/
├── server.json     # Modbus connection
├── zones.json      # Building structure
├── api.json        # API settings
└── features.json   # Feature flags
```

Quick start:

```bash
cp -r config.example config
# Edit config/server.json and config/zones.json
```

### 📁 Traditional Configuration

Single file approach (still supported):

```json
// data/config.json
{
  "server": { "type": "tcp", "address": "192.168.1.100", "port": 502 },
  "modbus": { "slave_id": 240 },
  "structures": [
    {
      "base_id": 1,
      "base_label": "First Floor",
      "zones": [
        { "id": 1, "label": "Living Room" },
        { "id": 2, "label": "Kitchen" }
      ]
    }
  ]
}
```

### 🔧 Environment Variables

For deployment-specific values and secrets:

```bash
# Development
export NEASMART_DEBUG_MODE=true
export NEASMART_LOG_LEVEL=DEBUG

# Production
export NEASMART_API_KEY=your-secret-key
export NEASMART_DEBUG_MODE=false
export NEASMART_DATABASE_PATH=/var/lib/neasmart/registers.db
```

**📖 Complete configuration guide:** [docs/guides/CONFIGURATION.md](docs/guides/CONFIGURATION.md)

## API Documentation

The gateway provides a RESTful API for monitoring and controlling your heating/cooling system:

- **Temperature monitoring** - Read current zone temperatures
- **Zone management** - Control individual zones and get labels
- **System health** - Monitor gateway and Modbus connection status
- **Pump operations** - Control and monitor circulation pumps
- **Mixed groups** - Handle complex zone configurations

**📖 Full API reference:** [docs/api/README.md](docs/api/README.md)

**🚀 Interactive API docs:** `http://localhost:5001/docs` (when running)

## Development

```bash
# Setup development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start development server with auto-reload
python src/main.py
```

**📖 Development guide:** [docs/development/SETUP.md](docs/development/SETUP.md)  
**📖 Quick commands:** [docs/development/QUICKSTART.md](docs/development/QUICKSTART.md)

## Documentation

- **[Configuration Guide](docs/guides/CONFIGURATION.md)** - Complete configuration reference
- **[API Documentation](docs/api/README.md)** - REST API reference
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System design and components
- **[Hardware Setup](docs/hardware/WAVESHARE_SETUP.md)** - Waveshare PoE Gateway setup
- **[Migration Guide](docs/guides/MIGRATION_GUIDE.md)** - Upgrading from older versions

**📖 All documentation:** [docs/README.md](docs/README.md)

## Features

- **Modbus TCP/Serial** - Connect via Ethernet or RS485
- **RESTful API** - JSON API with OpenAPI/Swagger documentation
- **Data Persistence** - SQLite database with automatic fallback
- **Circuit Breaker** - Automatic fault detection and recovery
- **Health Monitoring** - System status and diagnostics endpoints
- **Docker Support** - Production-ready containerized deployment
- **Temperature Control** - Multi-zone temperature management
- **Pump Control** - Circulation pump monitoring and control

## Troubleshooting

### Common Issues

**Gateway won't start:**

```bash
# Check configuration
python -c "from src.config import load_config; print('Config OK')"

# Check Modbus connection
telnet 192.168.1.100 502
```

**API not accessible:**

```bash
# Check if running
curl http://localhost:5001/health

# Check logs
tail -f data/gateway.log
```

**No zone data:**

- Verify `structures` array exists in `config.json`
- Check Modbus slave_id matches your device (usually 240 or 241)
- Ensure proper network connectivity to Modbus device

**📖 Complete troubleshooting:** [docs/guides/CONFIGURATION.md#troubleshooting](docs/guides/CONFIGURATION.md#troubleshooting)

## Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/development/SETUP.md) first.

## Support

- **Issues:** [GitHub Issues](https://github.com/your-username/RehauNeasmart2.0_Gateway/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-username/RehauNeasmart2.0_Gateway/discussions)

## License

MIT License - see LICENSE file for details.
