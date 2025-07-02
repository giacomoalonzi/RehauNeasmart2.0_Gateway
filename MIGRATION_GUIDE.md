# Migration Guide: v1 to v2

## Overview

This guide helps you migrate from the legacy `main.py` to the refactored `main.py` implementation.

## Key Changes

### 1. Architecture Improvements

#### v1 (Legacy)

- Single monolithic `main.py` file
- Global variables and context
- Basic error handling
- Flask development server

#### v2 (Refactored)

- Modular architecture with separate components
- Dependency injection and managers
- Comprehensive error handling with fallbacks
- Production-ready with Gunicorn support

### 2. Configuration

#### v1 Configuration

```json
{
  "gateway_address": "0.0.0.0",
  "gateway_port": "502",
  "server_type": "tcp",
  "slave_id": 240
}
```

#### v2 Configuration

```json
{
  "server": {
    "type": "tcp",
    "address": "192.168.1.100",
    "port": 502
  },
  "api": {
    "host": "0.0.0.0",
    "port": 5000,
    "enable_auth": false
  },
  "modbus": {
    "slave_id": 240,
    "sync_on_startup": true
  },
  "database": {
    "path": "./data/registers.db",
    "enable_fallback": true
  }
}
```

### 3. Environment Variables

v2 supports environment variables that override configuration:

```bash
# v1 had no environment variable support

# v2 environment variables
export NEASMART_SERVER_TYPE=tcp
export NEASMART_SERVER_ADDRESS=192.168.1.100
export NEASMART_MODBUS_SLAVE_ID=240
```

### 4. API Endpoints

All existing endpoints remain compatible, but with enhanced features:

| Endpoint               | v1    | v2       | Changes                           |
| ---------------------- | ----- | -------- | --------------------------------- |
| `/zones/<base>/<zone>` | ✓     | ✓        | Better error handling, validation |
| `/health`              | Basic | Enhanced | Detailed health status            |
| `/api/v1/*`            | ✗     | ✓        | New RESTful API                   |

### 5. Running the Application

#### v1 (Legacy)

```bash
cd src
python main.py
```

#### v2 (Development)

```bash
cd src
python main.py
```

#### v2 (Production)

```bash
# With Gunicorn (Python < 3.13)
gunicorn --config gunicorn_config.py main:app

# With Docker
docker-compose up -d
```

## Migration Steps

### Step 1: Backup Current Setup

```bash
# Backup database
cp data/registers.db data/registers.db.backup

# Backup configuration
cp data/options.json data/options.json.backup
```

### Step 2: Update Configuration

Convert your `options.json` to the new format:

```python
# Helper script to convert config
import json

# Read old config
with open('data/options.json', 'r') as f:
    old = json.load(f)

# Convert to new format
new = {
    "server": {
        "type": old.get("server_type", "tcp"),
        "address": old.get("gateway_address", "0.0.0.0"),
        "port": int(old.get("gateway_port", "502"))
    },
    "modbus": {
        "slave_id": old.get("slave_id", 240)
    },
    "api": {
        "host": "0.0.0.0",
        "port": 5001
    }
}

# Save new config
with open('data/config.json', 'w') as f:
    json.dump(new, f, indent=2)
```

### Step 3: Update Docker Setup

Update your `docker-compose.yml`:

```yaml
# Change the command from
CMD ["python3", "src/main.py"]

# To
CMD ["python3", "src/main.py"]
```

### Step 4: Test the Migration

1. Start the new version:

   ```bash
   python src/main.py
   ```

2. Test existing integrations:

   ```bash
   # Test zone endpoint
   curl http://localhost:5001/zones/1/1

   # Test health
   curl http://localhost:5001/health
   ```

3. Verify logs:
   ```bash
   tail -f data/gateway.log
   ```

### Step 5: Update Integrations

#### Home Assistant

No changes needed for existing integrations. The API remains compatible.

#### Monitoring

New Prometheus metrics available at `/metrics` (if enabled).

## Rollback Plan

If issues occur:

1. Stop the new version
2. Restore configuration:
   ```bash
   cp data/options.json.backup data/options.json
   cp data/registers.db.backup data/registers.db
   ```
3. Start the old version:
   ```bash
   python src/main.py
   ```

## Breaking Changes

### Removed Features

- Direct access to global `context` variable
- Manual threading management

### Changed Behavior

- Database now has automatic fallback
- Circuit breaker may delay responses during failures
- Structured JSON logging by default

## New Features in v2

1. **Reliability**

   - Circuit breaker pattern
   - Automatic fallbacks
   - Health monitoring

2. **Security**

   - API authentication (optional)
   - Rate limiting
   - CORS support

3. **Observability**

   - Structured logging
   - Metrics endpoint
   - Detailed health checks

4. **Performance**
   - Connection pooling
   - Caching layer
   - Async workers

## Troubleshooting

### Issue: Port already in use

```bash
# Find process using port
lsof -i :5001

# Kill process if needed
kill -9 <PID>
```

### Issue: Database locked

The new version handles this automatically with fallback to memory.

### Issue: Modbus connection fails

Check circuit breaker status in `/health` endpoint.

## Support

For migration support:

1. Check logs in `data/gateway.log`
2. Review health endpoint: `http://localhost:5001/health`
3. Enable debug mode: `NEASMART_LOG_LEVEL=DEBUG`
