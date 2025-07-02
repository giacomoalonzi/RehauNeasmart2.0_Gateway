# Implementation Notes - Rehau Neasmart 2.0 Gateway Refactoring

## Summary of Completed Work

We have created a robust foundation for the application with the following key components:

### 1. **Database Layer** (`database.py`)

- **Fallback Mechanism**: In-memory storage when SQLite fails
- **Automatic Retry**: Exponential backoff for transient failures
- **Health Monitoring**: Periodic connection checks
- **Thread Safety**: All operations protected with locks

### 2. **Modbus Management** (`modbus_manager.py`)

- **Circuit Breaker**: Prevents cascade failures
- **Cached Fallback**: Returns last known values when bus unavailable
- **Batch Sync**: Efficient synchronization from bus
- **Error Isolation**: Failures don't crash the application

### 3. **Configuration System** (`config.py`)

- **Flexible Loading**: File + environment variables
- **Validation**: Comprehensive input validation
- **Type Safety**: Dataclass-based configuration
- **Easy Override**: Environment vars override file config

### 4. **Production Server** (`gunicorn_config.py`)

- **Async Workers**: Gevent for high concurrency
- **Worker Management**: Auto-restart and recycling
- **Production Ready**: Proper timeouts and limits

## Migration Guide

### Step 1: Create New Main Application

Create `src/main_v2.py`:

```python
#!/usr/bin/env python3
"""
Rehau Neasmart 2.0 Gateway - Refactored Version
"""

import asyncio
import signal
import sys
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import get_config
from logger_setup import setup_logging
from database import get_database_manager
from modbus_manager import get_modbus_manager
from api.zones import zones_bp
# Import other blueprints...

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = get_config()

# Setup logging
setup_logging(config.logging)

# Initialize CORS
if config.api.enable_cors:
    CORS(app, origins=config.api.cors_origins)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"{config.api.rate_limit_per_minute} per minute"]
)

# Register blueprints
app.register_blueprint(zones_bp)
# Register other blueprints...

# Initialize managers
db_manager = get_database_manager(config.database.path)
modbus_manager = get_modbus_manager(config.modbus.slave_id)

# Sync on startup if configured
if config.modbus.sync_on_startup:
    modbus_manager.sync_from_bus()

async def run_modbus_server():
    """Run Modbus server"""
    # Your existing Modbus server code adapted to use modbus_manager
    pass

def signal_handler(sig, frame):
    """Graceful shutdown"""
    print("\nShutting down gracefully...")
    # Cleanup code
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run Modbus server in background
    asyncio.create_task(run_modbus_server())

    # Note: In production, use Gunicorn instead
    if config.debug_mode:
        app.run(host=config.api.host, port=config.api.port, debug=True)
```

### Step 2: Update Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ .

# Create data directory
RUN mkdir -p /app/data

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Use Gunicorn in production
CMD ["gunicorn", "--config", "gunicorn_config.py", "main_v2:app"]
```

### Step 3: Environment Configuration

Create `.env.example`:

```bash
# Server Configuration
NEASMART_SERVER_TYPE=tcp
NEASMART_SERVER_ADDRESS=0.0.0.0
NEASMART_SERVER_PORT=502

# API Configuration
NEASMART_API_HOST=0.0.0.0
NEASMART_API_PORT=5001
NEASMART_API_ENABLE_AUTH=false
NEASMART_API_KEY=your-secret-api-key

# Database Configuration
NEASMART_DATABASE_PATH=./data/registers.db
NEASMART_DATABASE_ENABLE_FALLBACK=true

# Modbus Configuration
NEASMART_MODBUS_SLAVE_ID=240
NEASMART_MODBUS_SYNC_ON_STARTUP=true

# Logging
NEASMART_LOG_LEVEL=INFO
NEASMART_LOG_FILE=./data/gateway.log
LOG_FORMAT=json

# Production
ENVIRONMENT=production
NEASMART_WORKERS=4
```

## API Documentation Example

Create `src/api/swagger.py`:

```python
from flasgger import Swagger

def init_swagger(app):
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }

    swagger = Swagger(app, config=swagger_config)
    return swagger
```

## Middleware Implementation

Create `src/middleware.py`:

```python
import time
from flask import request, g
from functools import wraps
from logger_setup import log_api_request

def request_logging_middleware(app):
    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration_ms = (time.time() - g.start_time) * 1000
            log_api_request(
                app.logger,
                request.method,
                request.path,
                response.status_code,
                duration_ms
            )
        return response

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != app.config['API_KEY']:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

## Testing Strategy

### Unit Test Example

Create `tests/test_database.py`:

```python
import pytest
from src.database import DatabaseManager, InMemoryFallback

def test_fallback_mechanism():
    """Test that fallback works when database fails"""
    fallback = InMemoryFallback()
    fallback.set(100, 42)
    assert fallback.get(100) == 42

def test_database_retry():
    """Test retry logic"""
    # Mock failing database
    # Test that retry attempts are made
    pass
```

## Monitoring Setup

### Prometheus Metrics

Create `src/metrics.py`:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

modbus_errors_total = Counter(
    'modbus_errors_total',
    'Total Modbus errors',
    ['operation', 'error_type']
)

circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half-open)'
)
```

## Performance Optimizations

1. **Connection Pooling**: Already implemented in database layer
2. **Caching**: Add Redis for frequently accessed data
3. **Async Operations**: Use gevent for concurrent requests
4. **Batch Operations**: Group Modbus reads/writes

## Security Checklist

- [ ] Enable API authentication in production
- [ ] Use HTTPS for API endpoints
- [ ] Implement request signing for critical operations
- [ ] Add audit logging for all write operations
- [ ] Regular security dependency updates
- [ ] Input validation on all endpoints
- [ ] Rate limiting per user/IP

## Deployment Checklist

1. **Pre-deployment**

   - [ ] Run all tests
   - [ ] Check configuration
   - [ ] Verify database migrations
   - [ ] Test fallback mechanisms

2. **Deployment**

   - [ ] Deploy with blue-green strategy
   - [ ] Monitor error rates
   - [ ] Check circuit breaker status
   - [ ] Verify logging output

3. **Post-deployment**
   - [ ] Monitor performance metrics
   - [ ] Check for memory leaks
   - [ ] Verify data consistency
   - [ ] Test failover scenarios

## Common Issues and Solutions

### Issue: Circuit breaker opens frequently

**Solution**: Adjust threshold and timeout in config

```python
circuit_breaker_failure_threshold: 10  # Increase threshold
circuit_breaker_recovery_timeout: 120  # Longer recovery
```

### Issue: Database performance degradation

**Solution**: Use in-memory fallback and schedule maintenance

```python
# Check database status
status = db_manager.get_status()
if status['healthy'] == False:
    # Alert and use fallback
    pass
```

### Issue: High memory usage with fallback

**Solution**: Implement LRU cache with size limit

```python
from cachetools import LRUCache
# Limit fallback size
```

## Next Development Priorities

1. **Week 1**: Complete main_v2.py and test migration
2. **Week 2**: Add remaining API endpoints as blueprints
3. **Week 3**: Implement authentication and authorization
4. **Week 4**: Add comprehensive test suite
5. **Week 5**: Performance testing and optimization
6. **Week 6**: Documentation and deployment guide

## Contact and Support

For questions about this refactoring:

- Review the code comments
- Check the API documentation
- Run the test suite
- Monitor the logs

Remember: The goal is zero downtime and improved reliability!
