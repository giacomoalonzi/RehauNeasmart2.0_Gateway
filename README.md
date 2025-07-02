# Rehau Neasmart 2.0 Gateway

> **Production-Ready Gateway**: A robust, enterprise-grade bridge between Rehau Neasmart 2.0 SysBus (Modbus variant) and Home Assistant. Features comprehensive error handling, automatic fallbacks, and production-ready deployment.

[![Docker](https://img.shields.io/badge/docker-supported-blue)](https://www.docker.com/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

### Core Functionality

- **REST API** with versioning and comprehensive error handling
- **Modbus TCP and Serial (RS485)** support with automatic reconnection
- **Persistent Storage** with SQLite and in-memory fallback
- **Real-time Data** synchronization with configurable intervals
- **Production-Ready** with Gunicorn and proper logging

### 🛡️ Robustness & Reliability

- **Circuit Breaker Pattern** - Prevents cascade failures
- **Automatic Fallbacks** - In-memory storage when database fails
- **Retry Logic** - Exponential backoff for transient failures
- **Health Monitoring** - Continuous connection health checks
- **Thread-Safe Operations** - Concurrent request handling
- **Zero-Downtime Recovery** - Graceful error handling and recovery

### 🔧 Production Features

- **Structured Logging** - JSON format with rotation and multiple handlers
- **Configuration Management** - File and environment variable support
- **API Authentication** - JWT and API key support (configurable)
- **Rate Limiting** - Protection against API abuse
- **CORS Support** - Cross-origin resource sharing
- **Monitoring Ready** - Prometheus metrics and health endpoints
- **Docker Optimized** - Multi-stage builds and security best practices

---

## 🏗️ Refactored Architecture (v2)

The gateway has been completely refactored for production readiness. The new architecture includes:

### Core Components

1. **Database Manager** (`database.py`)

   - Thread-safe SQLite operations with connection pooling
   - Automatic retry with exponential backoff
   - In-memory fallback when database is unavailable
   - Transaction support and health monitoring

2. **Modbus Manager** (`modbus_manager.py`)

   - Circuit breaker pattern for fault tolerance
   - Thread-safe context management
   - Automatic reconnection and error recovery
   - Batch synchronization capabilities

3. **Configuration System** (`config.py`)

   - Dual configuration support (file + environment variables)
   - Schema validation with detailed error messages
   - Hot-reload capability for dynamic updates
   - Type-safe configuration objects

4. **Logging Infrastructure** (`logger_setup.py`)

   - Structured logging with JSON support
   - Multiple handlers (console, file, syslog)
   - Log rotation and compression
   - Request/response tracking with correlation IDs

5. **API Layer** (`api/zones.py`)
   - RESTful endpoints with proper error handling
   - Input validation and sanitization
   - Comprehensive error responses
   - Blueprint-based modular structure

### Key Improvements Over v1

- **Reliability**: Circuit breaker prevents cascade failures
- **Performance**: Connection pooling and caching
- **Observability**: Structured logging and health endpoints
- **Security**: API authentication and rate limiting
- **Maintainability**: Modular architecture with clear separation of concerns

---

## 📋 Quick Start

### Prerequisites

- Docker and Docker Compose
- Access to Rehau Neasmart 2.0 SysBus interface
- Optional: RS485-to-TCP adapter (e.g., Waveshare RS485 PoE Gateway)

### Quick Installation (Linux/macOS)

For a quick setup, use the installation helper script:

```bash
git clone https://github.com/your-username/RehauNeasmart2.0_Gateway.git
cd RehauNeasmart2.0_Gateway
chmod +x install.sh
./install.sh
```

This script will:

- Create a virtual environment
- Install all dependencies
- Create the data directory
- Generate a default configuration file

### Docker Deployment (Recommended)

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/RehauNeasmart2.0_Gateway.git
   cd RehauNeasmart2.0_Gateway
   ```

2. **Configure Environment**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Deploy with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

### Manual Installation

1. **Setup Python Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   # Install all required dependencies including the refactored components
   pip install -r requirements.txt
   ```

2. **Configure Application**:

   There are two ways to configure the application:

   **Option A: Using configuration file (recommended)**

   Create or modify `data/config.json`:

   ```json
   {
     "server": {
       "type": "tcp",
       "address": "192.168.1.100",
       "port": 502
     },
     "modbus": {
       "slave_id": 240,
       "sync_on_startup": true
     },
     "api": {
       "host": "0.0.0.0",
       "port": 5001,
       "enable_auth": false
     }
   }
   ```

   **Option B: Using environment variables**

   ```bash
   export NEASMART_SERVER_TYPE=tcp
   export NEASMART_SERVER_ADDRESS=192.168.1.100
   export NEASMART_MODBUS_SLAVE_ID=240
   ```

3. **Run Application**:

   ```bash
   cd src
   # Development mode (with debug enabled)
   python main_v2.py

   # Production mode with Gunicorn (Python < 3.13)
   # Note: Gunicorn is currently disabled for Python 3.13 compatibility
   # Uncomment gunicorn in requirements.txt first if using Python < 3.13
   gunicorn --config gunicorn_config.py main_v2:app
   ```

---

## 🔧 Configuration

### Environment Variables

The gateway supports comprehensive configuration via environment variables:

#### Core Configuration

| Variable                   | Description           | Default   | Example         |
| -------------------------- | --------------------- | --------- | --------------- |
| `NEASMART_SERVER_TYPE`     | Connection type       | `tcp`     | `tcp`, `serial` |
| `NEASMART_SERVER_ADDRESS`  | Modbus server address | `0.0.0.0` | `192.168.1.100` |
| `NEASMART_SERVER_PORT`     | Modbus server port    | `502`     | `502`           |
| `NEASMART_MODBUS_SLAVE_ID` | Modbus slave ID       | `240`     | `240`, `241`    |

#### API Configuration

| Variable                   | Description                | Default   | Example           |
| -------------------------- | -------------------------- | --------- | ----------------- |
| `NEASMART_API_HOST`        | API bind address           | `0.0.0.0` | `0.0.0.0`         |
| `NEASMART_API_PORT`        | API port                   | `5001`    | `5001`            |
| `NEASMART_API_ENABLE_AUTH` | Enable authentication      | `false`   | `true`            |
| `NEASMART_API_KEY`         | API key for authentication | -         | `your-secret-key` |
| `NEASMART_API_JWT_SECRET`  | JWT secret key             | -         | `your-jwt-secret` |

#### Database Configuration

| Variable                            | Description               | Default               | Example                  |
| ----------------------------------- | ------------------------- | --------------------- | ------------------------ |
| `NEASMART_DATABASE_PATH`            | Database file path        | `./data/registers.db` | `/app/data/registers.db` |
| `NEASMART_DATABASE_ENABLE_FALLBACK` | Enable in-memory fallback | `true`                | `true`                   |

#### Logging Configuration

| Variable             | Description   | Default              | Example                    |
| -------------------- | ------------- | -------------------- | -------------------------- |
| `NEASMART_LOG_LEVEL` | Logging level | `INFO`               | `DEBUG`, `INFO`, `WARNING` |
| `NEASMART_LOG_FILE`  | Log file path | `./data/gateway.log` | `/app/logs/gateway.log`    |
| `LOG_FORMAT`         | Log format    | `text`               | `json`, `text`             |

#### Production Configuration

| Variable           | Description      | Default      | Example                  |
| ------------------ | ---------------- | ------------ | ------------------------ |
| `NEASMART_WORKERS` | Gunicorn workers | `4`          | `8`                      |
| `ENVIRONMENT`      | Environment name | `production` | `development`, `staging` |

### Configuration File

Alternatively, create a `config.json` file:

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
    "circuit_breaker_failure_threshold": 5
  },
  "api": {
    "host": "0.0.0.0",
    "port": 5001,
    "enable_auth": false,
    "rate_limit_per_minute": 60
  },
  "database": {
    "path": "./data/registers.db",
    "enable_fallback": true
  },
  "logging": {
    "level": "INFO",
    "enable_file": true,
    "file_path": "./data/gateway.log"
  }
}
```

---

## 🌐 API Reference

### Base URL

- Development: `http://localhost:5001/api/v1`
- Production: `https://your-domain.com/api/v1`

### Authentication

When authentication is enabled, include the API key in headers:

```bash
curl -H "X-API-Key: your-api-key" \
     -X GET http://localhost:5001/api/v1/zones/1/1
```

### Endpoints

#### System Status

**GET** `/health`

- **Description**: Gateway health check with detailed status
- **Response**:
  ```json
  {
    "status": "healthy",
    "database": {
      "healthy": true,
      "using_fallback": false
    },
    "modbus": {
      "circuit_breaker_state": "closed",
      "context_initialized": true
    },
    "uptime": 3600,
    "version": "2.0.0"
  }
  ```

#### Zone Management

**GET** `/zones/<base_id>/<zone_id>`

- **Description**: Get specific zone information
- **Parameters**:
  - `base_id`: Base ID (1-4)
  - `zone_id`: Zone ID (1-12)
- **Response**:
  ```json
  {
    "base_id": 1,
    "zone_id": 1,
    "state": 3,
    "setpoint": 21.5,
    "temperature": 22.0,
    "relative_humidity": 45,
    "address": 1300,
    "active": true
  }
  ```

**POST** `/zones/<base_id>/<zone_id>`

- **Description**: Update zone parameters
- **Body**:
  ```json
  {
    "state": 3,
    "setpoint": 22.5
  }
  ```
- **Response**:
  ```json
  {
    "base_id": 1,
    "zone_id": 1,
    "updated": {
      "state": 3,
      "setpoint": 22.5,
      "setpoint_encoded": 28729
    }
  }
  ```

**GET** `/zones/`

- **Description**: List all zones
- **Query Parameters**:
  - `base_id`: Filter by base ID (optional)
  - `include_inactive`: Include inactive zones (default: false)
- **Response**:
  ```json
  {
    "zones": [...],
    "count": 8,
    "filter": {
      "base_id": null,
      "include_inactive": false
    }
  }
  ```

#### System Information

**GET** `/outsidetemperature`

- **Description**: Get outside temperature readings
- **Response**:
  ```json
  {
    "outside_temperature": 15.2,
    "filtered_outside_temperature": 15.0
  }
  ```

**GET** `/notifications`

- **Description**: Get system notifications
- **Response**:
  ```json
  {
    "hints_present": false,
    "warnings_present": true,
    "error_present": false
  }
  ```

**GET** `/mode`

- **Description**: Get global operation mode
  **POST** `/mode`
- **Description**: Set global operation mode
- **Body**: `{"mode": 2}`

**GET** `/state`

- **Description**: Get global operation state
  **POST** `/state`
- **Description**: Set global operation state
- **Body**: `{"state": 1}`

#### Mixed Groups & Equipment

**GET** `/mixedgroups/<group_id>`

- **Description**: Get mixed circuit information
- **Parameters**: `group_id` (1-3)

**GET** `/dehumidifiers/<dehumidifier_id>`

- **Description**: Get dehumidifier status
- **Parameters**: `dehumidifier_id` (1-9)

**GET** `/pumps/<pump_id>`

- **Description**: Get extra pump status
- **Parameters**: `pump_id` (1-5)

### Error Responses

All API errors follow a consistent format:

```json
{
  "error": "Invalid zone ID: 15. Must be between 1 and 12",
  "status": 400,
  "details": "Validation failed for parameter zone_id"
}
```

**HTTP Status Codes**:

- `200`: Success
- `400`: Bad Request (validation error)
- `401`: Unauthorized (authentication required)
- `404`: Not Found
- `429`: Too Many Requests (rate limited)
- `500`: Internal Server Error
- `503`: Service Unavailable (Modbus communication error)

---

## 🛡️ Reliability & Error Handling

### Circuit Breaker Pattern

The gateway implements a circuit breaker to prevent cascade failures:

- **Closed State**: Normal operation
- **Open State**: Stops requests after failure threshold (default: 5 failures)
- **Half-Open State**: Tests service recovery

When the circuit breaker is open, the gateway returns cached values from the database.

### Automatic Fallbacks

1. **Database Fallback**: If SQLite fails, data is stored in memory
2. **Modbus Fallback**: If bus communication fails, returns last known values
3. **Service Degradation**: API continues working even with partial failures

### Data Synchronization

- **Startup Sync**: Optionally sync all values from Modbus on startup
- **Periodic Sync**: Configurable intervals for data freshness
- **Event-Driven**: Updates are immediately persisted to database
- **Conflict Resolution**: Last-write-wins strategy

---

## 📊 Monitoring & Observability

### Health Checks

The gateway provides detailed health information:

```bash
curl http://localhost:5001/health
```

### Logging

Structured logging with multiple output formats:

```bash
# JSON format (production)
export LOG_FORMAT=json

# Human-readable format (development)
export LOG_FORMAT=text
```

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### Metrics (Optional)

Prometheus metrics available at `/metrics`:

- API request duration and count
- Modbus operation success/failure rates
- Circuit breaker state
- Database operation metrics

---

## 🐳 Docker Deployment

### Docker Compose

```yaml
version: '3.8'

services:
  neasmart-gateway:
    image: rehauneasmart-gateway:latest
    ports:
      - '502:502' # Modbus
      - '5001:5001' # API
    environment:
      - NEASMART_SERVER_TYPE=tcp
      - NEASMART_SERVER_ADDRESS=192.168.1.100
      - NEASMART_MODBUS_SLAVE_ID=240
      - NEASMART_API_ENABLE_AUTH=true
      - NEASMART_API_KEY=your-secret-key
      - LOG_FORMAT=json
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:5001/health']
      interval: 30s
      timeout: 10s
      retries: 3
```

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ .

# Create directories
RUN mkdir -p /app/data /app/logs

# Security: non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Production server
CMD ["gunicorn", "--config", "gunicorn_config.py", "main_v2:app"]
```

---

## 🧪 Testing

### Unit Tests

```bash
cd src
python -m pytest tests/ -v --cov=. --cov-report=html
```

### Integration Tests

```bash
# Test API endpoints
python -m pytest tests/test_api.py -v

# Test Modbus communication
python -m pytest tests/test_modbus.py -v
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:5001/api/v1/zones/1/1

# Using Artillery
artillery run tests/load-test.yml
```

---

## 🔧 Development

### Project Structure

```
src/
├── api/                    # API blueprints
│   ├── __init__.py
│   ├── zones.py           # Zone endpoints
│   └── ...
├── config.py              # Configuration management
├── database.py            # Database abstraction layer
├── modbus_manager.py      # Modbus management
├── logger_setup.py        # Logging configuration
├── gunicorn_config.py     # Production server config
├── main_v2.py             # Main application (new)
├── main.py                # Legacy application
└── requirements.txt       # Dependencies

tests/
├── test_database.py       # Database tests
├── test_modbus.py         # Modbus tests
├── test_api.py            # API tests
└── ...

data/                      # Persistent data
├── registers.db           # SQLite database
├── config.json            # Configuration file
└── gateway.log            # Application logs
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## ⚙️ Migration from v1

### Automated Migration

```bash
# Run migration script
python migrate_to_v2.py

# Test new version
python -m pytest tests/

# Switch to new version
docker-compose down
docker-compose -f docker-compose-v2.yml up -d
```

### Manual Migration

1. **Backup existing data**:

   ```bash
   cp data/registers.db data/registers.db.backup
   ```

2. **Update configuration**:

   ```bash
   # Convert old environment variables
   # OLD: gateway_address -> NEW: NEASMART_SERVER_ADDRESS
   # OLD: SERVER_TYPE -> NEW: NEASMART_SERVER_TYPE
   ```

3. **Test compatibility**:
   ```bash
   # Verify API compatibility
   curl http://localhost:5001/api/v1/zones/1/1
   ```

---

## 🐛 Troubleshooting

### Installation Issues

#### ModuleNotFoundError: No module named 'flask_cors'

This error occurs when dependencies are installed from the wrong requirements file.

**Solution**:

```bash
# Make sure to install from the root requirements.txt, not src/requirements.txt
pip install -r requirements.txt
```

#### Python 3.13 Compatibility

Gunicorn and gevent are currently incompatible with Python 3.13. For development:

```bash
# Use the built-in Flask server
python src/main_v2.py
```

For production with Python 3.13, consider using alternative WSGI servers like waitress:

```bash
pip install waitress
waitress-serve --port=5001 --call 'main_v2:create_app'
```

### Port Conflicts

If you get errors about ports being already in use:

#### Option 1: Use Different Ports

Edit `data/config.json` to use different ports:

```json
{
  "server": {
    "port": 5502 // Instead of 502
  },
  "api": {
    "port": 5501 // Instead of 5001
  }
}
```

#### Option 2: Stop Existing Services

Find and stop processes using the ports:

```bash
# Find processes
lsof -i :502,5001 | grep LISTEN

# Stop the old gateway
pkill -f "python.*main.py"
```

### Common Issues

#### Circuit Breaker Opens Frequently

```bash
# Check Modbus connectivity
curl http://localhost:5001/health

# Adjust circuit breaker settings
export NEASMART_MODBUS_CIRCUIT_BREAKER_FAILURE_THRESHOLD=10
export NEASMART_MODBUS_CIRCUIT_BREAKER_RECOVERY_TIMEOUT=120
```

#### Database Performance Issues

```bash
# Enable fallback mode
export NEASMART_DATABASE_ENABLE_FALLBACK=true

# Check database status
curl http://localhost:5001/health | jq '.database'
```

#### High Memory Usage

```bash
# Monitor fallback usage
curl http://localhost:5001/health | jq '.database.fallback_entries'

# Reduce worker count
export NEASMART_WORKERS=2
```

### Debug Mode

```bash
# Enable debug logging
export NEASMART_LOG_LEVEL=DEBUG
export NEASMART_DEBUG_MODE=true

# Check logs
tail -f data/gateway.log
```

### Health Monitoring

```bash
# Comprehensive health check
curl -s http://localhost:5001/health | jq

# Circuit breaker status
curl -s http://localhost:5001/health | jq '.modbus.circuit_breaker'

# Database status
curl -s http://localhost:5001/health | jq '.database'
```

---

## 📚 Additional Resources

- **[API Documentation](http://localhost:5001/api/docs)** - Interactive Swagger UI
- **[Configuration Guide](data/CONFIG_GUIDE.md)** - Detailed configuration reference
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment best practices
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions
- **[Contributing Guide](CONTRIBUTING.md)** - Development guidelines
- **[Refactoring Checklist](REFACTORING_CHECKLIST.md)** - Implementation status and roadmap

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/RehauNeasmart2.0_Gateway/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/RehauNeasmart2.0_Gateway/discussions)
- **Wiki**: [Project Wiki](https://github.com/your-username/RehauNeasmart2.0_Gateway/wiki)

---

## ✨ Acknowledgments

- Original project by [MatteoManzoni](https://github.com/MatteoManzoni/RehauNeasmart2.0_Gateway)
- Rehau for the Neasmart 2.0 system
- Open source community for excellent tools and libraries
