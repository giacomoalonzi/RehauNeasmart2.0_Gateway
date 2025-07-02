# Architecture Documentation

## Overview

The Rehau Neasmart 2.0 Gateway follows a modular, production-ready architecture designed for reliability, maintainability, and scalability.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     External Systems                         │
├─────────────────────────────────────────────────────────────┤
│  Home Assistant  │  Web Clients  │  Monitoring Systems      │
└────────┬─────────┴───────┬───────┴────────┬─────────────────┘
         │                 │                 │
         └─────────────────┴─────────────────┘
                           │
                    ┌──────▼──────┐
                    │   REST API   │
                    │  (Flask App) │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼─────┐    ┌──────▼──────┐   ┌─────▼─────┐
    │  Config  │    │   Database  │   │  Modbus   │
    │ Manager  │    │   Manager   │   │  Manager  │
    └──────────┘    └──────┬──────┘   └─────┬─────┘
                           │                 │
                    ┌──────▼──────┐   ┌─────▼─────┐
                    │   SQLite    │   │  Modbus   │
                    │  Database   │   │  Context  │
                    └─────────────┘   └─────┬─────┘
                                           │
                                    ┌──────▼──────┐
                                    │ NEA SMART   │
                                    │ 2.0 System  │
                                    └─────────────┘
```

## Core Components

### 1. Configuration Manager (`config.py`)

Manages all application configuration with multiple sources:

- **File-based**: JSON configuration files
- **Environment Variables**: Override file settings
- **Validation**: Schema validation with detailed errors
- **Type Safety**: Dataclass-based configuration objects

### 2. Database Manager (`database.py`)

Provides reliable data persistence with fallback mechanisms:

- **Primary Storage**: SQLite with connection pooling
- **Fallback Storage**: In-memory cache when database fails
- **Retry Logic**: Exponential backoff for transient failures
- **Health Monitoring**: Automatic health checks
- **Thread Safety**: All operations are thread-safe

### 3. Modbus Manager (`modbus_manager.py`)

Handles all Modbus communication with the heating system:

- **Circuit Breaker**: Prevents cascade failures
- **Context Management**: Thread-safe Modbus context
- **Caching**: Returns cached values when bus unavailable
- **Batch Operations**: Efficient bulk read/write
- **Error Recovery**: Automatic reconnection

### 4. API Layer (`api/`)

RESTful API implementation:

- **Flask Blueprints**: Modular endpoint organization
- **Input Validation**: Request validation and sanitization
- **Error Handling**: Comprehensive error responses
- **Authentication**: Optional API key/JWT support
- **Rate Limiting**: Protection against abuse

### 5. Logging Infrastructure (`logger_setup.py`)

Structured logging for production environments:

- **JSON Logging**: Machine-readable log format
- **Multiple Handlers**: Console, file, syslog support
- **Log Rotation**: Automatic log file rotation
- **Context Injection**: Request ID tracking
- **Performance Metrics**: Request timing

## Data Flow

### Read Operations

1. Client sends GET request to API endpoint
2. API validates request parameters
3. API queries Modbus Manager for current values
4. Modbus Manager checks circuit breaker state
5. If healthy: Read from Modbus bus
6. If unhealthy: Return cached value from database
7. Update database with latest values
8. Return formatted response to client

### Write Operations

1. Client sends POST request with new values
2. API validates and sanitizes input
3. API sends write command to Modbus Manager
4. Modbus Manager writes to bus (with retry)
5. Database updated with new values
6. Confirmation response sent to client

## Reliability Mechanisms

### Circuit Breaker Pattern

```
CLOSED → [failures exceed threshold] → OPEN
  ↑                                      ↓
  ← HALF-OPEN ← [timeout expires] ←─────┘
```

- **Closed**: Normal operation
- **Open**: All requests fail fast
- **Half-Open**: Test if service recovered

### Fallback Strategy

1. **Primary**: Direct Modbus communication
2. **Secondary**: Database cached values
3. **Tertiary**: In-memory fallback storage

### Error Recovery

- **Automatic Retry**: With exponential backoff
- **Graceful Degradation**: Partial functionality maintained
- **Health Monitoring**: Continuous health checks
- **Self-Healing**: Automatic recovery attempts

## Security Considerations

### API Security

- **Authentication**: API key or JWT tokens
- **Rate Limiting**: Per-IP request limits
- **Input Validation**: Strict parameter validation
- **CORS**: Configurable cross-origin policies

### System Security

- **No Root**: Container runs as non-root user
- **Network Isolation**: Minimal exposed ports
- **Secrets Management**: Environment variables
- **Audit Logging**: All write operations logged

## Performance Optimizations

### Caching

- **Database Cache**: Frequently accessed values
- **In-Memory Cache**: LRU cache for hot data
- **Response Cache**: HTTP caching headers

### Concurrency

- **Async Workers**: Gevent for high concurrency
- **Connection Pooling**: Database connections
- **Thread Safety**: Lock-free where possible

### Resource Management

- **Worker Recycling**: Prevent memory leaks
- **Connection Limits**: Prevent exhaustion
- **Graceful Shutdown**: Clean resource cleanup

## Deployment Architecture

### Docker Container

```dockerfile
# Multi-stage build
FROM python:3.9-slim AS builder
# Build dependencies

FROM python:3.9-slim
# Runtime only
```

### Health Checks

- **/health**: Application health
- **Database**: Connection status
- **Modbus**: Communication status
- **Memory**: Usage monitoring

### Monitoring Integration

- **Prometheus Metrics**: Performance metrics
- **Structured Logs**: JSON format
- **Health Endpoints**: Status monitoring
- **Error Tracking**: Exception reporting

## Configuration Options

### Environment Variables

```bash
# Server Configuration
NEASMART_GATEWAY_SERVER_TYPE=tcp
NEASMART_GATEWAY_SERVER_ADDRESS=192.168.1.100
NEASMART_GATEWAY_SERVER_PORT=502

# API Configuration
NEASMART_API_PORT=5000
NEASMART_API_ENABLE_AUTH=true

# Database Configuration
NEASMART_DATABASE_PATH=/data/registers.db
NEASMART_DATABASE_ENABLE_FALLBACK=true

# Modbus Configuration
NEASMART_MODBUS_SLAVE_ID=240
NEASMART_MODBUS_SYNC_ON_STARTUP=true
```

### Configuration File

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
  }
}
```

## Future Enhancements

### Planned Features

1. **WebSocket Support**: Real-time updates
2. **MQTT Integration**: IoT protocol support
3. **Multi-Gateway**: Support multiple systems
4. **Cloud Sync**: Remote monitoring
5. **Machine Learning**: Predictive control

### Architecture Evolution

- **Microservices**: Split into smaller services
- **Event Sourcing**: Complete audit trail
- **GraphQL API**: Flexible queries
- **Kubernetes**: Container orchestration
