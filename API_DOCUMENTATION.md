# API Documentation - Rehau Neasmart 2.0 Gateway

## Overview

The Rehau Neasmart 2.0 Gateway provides a RESTful API for interacting with the heating system. The API supports both legacy endpoints (for backward compatibility) and new versioned endpoints following REST best practices.

## Base URLs

- **Local**: `http://localhost:5000`
- **Docker**: `http://<container-ip>:5000`
- **Production**: `https://<your-domain>/api`

## Authentication

When authentication is enabled (`NEASMART_API_ENABLE_AUTH=true`), all requests must include an API key:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:5000/api/v1/zones
```

## Common Response Formats

### Success Response

```json
{
  "data": {...},
  "status": "success",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### Error Response

```json
{
  "error": "Description of the error",
  "status": 400,
  "details": "Additional error information",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

## Endpoints

### System Health

#### GET /health

Check the gateway health status.

**Response:**

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database": {
    "healthy": true,
    "using_fallback": false,
    "entries": 1234
  },
  "modbus": {
    "circuit_breaker_state": "closed",
    "context_initialized": true,
    "last_sync": "2024-01-20T10:25:00Z"
  },
  "uptime": 3600
}
```

### Zone Management

#### GET /api/v1/zones

List all zones with their current status.

**Query Parameters:**

- `base_id` (optional): Filter by base ID (1-4)
- `include_inactive` (optional): Include inactive zones (default: false)

**Response:**

```json
{
  "zones": [
    {
      "base_id": 1,
      "zone_id": 1,
      "name": "Living Room",
      "temperature": 21.5,
      "humidity": 45,
      "setpoint": 22.0,
      "state": 3,
      "active": true
    }
  ],
  "count": 12,
  "filter": {
    "base_id": null,
    "include_inactive": false
  }
}
```

#### GET /api/v1/zones/{base_id}/{zone_id}

Get specific zone information.

**Parameters:**

- `base_id`: Base ID (1-4)
- `zone_id`: Zone ID (1-12)

**Response:**

```json
{
  "base_id": 1,
  "zone_id": 1,
  "name": "Living Room",
  "state": 3,
  "setpoint": 21.5,
  "temperature": 22.0,
  "relative_humidity": 45,
  "address": 1300,
  "active": true,
  "last_update": "2024-01-20T10:28:00Z"
}
```

#### POST /api/v1/zones/{base_id}/{zone_id}

Update zone parameters.

**Request Body:**

```json
{
  "state": 3,
  "setpoint": 22.5
}
```

**State Values:**

- `1`: Economy
- `2`: Comfort
- `3`: Auto
- `4`: Night
- `5`: Holiday
- `6`: Off

**Response:**

```json
{
  "base_id": 1,
  "zone_id": 1,
  "updated": {
    "state": 3,
    "setpoint": 22.5,
    "setpoint_encoded": 28729
  },
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### System Information

#### GET /outsidetemperature

Get outside temperature readings.

**Response:**

```json
{
  "outside_temperature": 15.2,
  "filtered_outside_temperature": 15.0
}
```

#### GET /notifications

Get system notifications status.

**Response:**

```json
{
  "hints_present": false,
  "warnings_present": true,
  "error_present": false
}
```

### Global Controls

#### GET /mode

Get global operation mode.

**Response:**

```json
{
  "mode": 2
}
```

**Mode Values:**

- `1`: Heating
- `2`: Cooling
- `3`: Auto
- `4`: Ventilation
- `5`: Dehumidification

#### POST /mode

Set global operation mode.

**Request Body:**

```json
{
  "mode": 2
}
```

#### GET /state

Get global operation state.

**Response:**

```json
{
  "state": 1
}
```

#### POST /state

Set global operation state.

**Request Body:**

```json
{
  "state": 1
}
```

### Equipment Status

#### GET /mixedgroups/{group_id}

Get mixed circuit information.

**Parameters:**

- `group_id`: Mixed group ID (1-3)

**Response:**

```json
{
  "group_id": 1,
  "pump_state": 1,
  "mixing_valve_opening_percentage": 75,
  "flow_temperature": 35.5,
  "return_temperature": 28.3
}
```

#### GET /dehumidifiers/{dehumidifier_id}

Get dehumidifier status.

**Parameters:**

- `dehumidifier_id`: Dehumidifier ID (1-9)

**Response:**

```json
{
  "dehumidifier_id": 1,
  "dehumidifier_state": 1
}
```

#### GET /pumps/{pump_id}

Get extra pump status.

**Parameters:**

- `pump_id`: Pump ID (1-5)

**Response:**

```json
{
  "pump_id": 1,
  "pump_state": 1
}
```

## Rate Limiting

When rate limiting is enabled, the API limits requests per IP address:

- Default: 60 requests per minute
- Headers returned:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

## Error Codes

| Code | Description                                      |
| ---- | ------------------------------------------------ |
| 400  | Bad Request - Invalid parameters                 |
| 401  | Unauthorized - Invalid or missing API key        |
| 404  | Not Found - Resource not found                   |
| 429  | Too Many Requests - Rate limit exceeded          |
| 500  | Internal Server Error                            |
| 503  | Service Unavailable - Modbus communication error |

## WebSocket Support (Future)

Future versions will support WebSocket connections for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:5000/ws');
ws.on('message', (data) => {
  console.log('Zone update:', JSON.parse(data));
});
```

## Examples

### Python

```python
import requests

# Get all zones
response = requests.get('http://localhost:5000/api/v1/zones')
zones = response.json()

# Update zone setpoint
data = {'setpoint': 22.5}
response = requests.post('http://localhost:5000/api/v1/zones/1/1', json=data)
```

### cURL

```bash
# Get zone information
curl http://localhost:5000/api/v1/zones/1/1

# Update zone state
curl -X POST http://localhost:5000/api/v1/zones/1/1 \
  -H "Content-Type: application/json" \
  -d '{"state": 3, "setpoint": 22.0}'
```

### Home Assistant REST Integration

```yaml
rest_command:
  set_zone_temperature:
    url: 'http://gateway-ip:5000/api/v1/zones/{{ base_id }}/{{ zone_id }}'
    method: POST
    headers:
      Content-Type: application/json
    payload: '{"setpoint": {{ temperature }}}'
```
