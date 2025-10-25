# API-Modbus Interaction Architecture

## Overview

The Rehau Neasmart 2.0 Gateway implements a sophisticated architecture where a Flask REST API interacts with both a Modbus server and Modbus client to provide seamless communication with the physical Neasmart device. This document explains how these components work together to enable real-time control and monitoring of the heating/cooling system.

## Architecture Components

### 1. Flask REST API Server
- **Purpose**: Provides HTTP endpoints for external clients to interact with the system
- **Location**: `src/main.py`, `src/app_factory.py`
- **Port**: Configurable (default: 5001)
- **Features**: 
  - RESTful endpoints for zones, devices, temperature, operation modes
  - OpenAPI/Swagger documentation
  - JSON request/response format

### 2. Modbus Server
- **Purpose**: Acts as a Modbus TCP/RTU server that exposes system data
- **Location**: `src/modbus_server.py`
- **Features**:
  - Thread-safe persistent data storage using SQLite
  - Support for both TCP and Serial (RTU) connections
  - Real-time register monitoring and logging
  - Broadcast support for multiple clients

### 3. Modbus Client
- **Purpose**: Writes setpoints directly to the physical Neasmart device
- **Location**: `src/modbus_client.py`
- **Features**:
  - Async Modbus TCP client for Waveshare gateway communication
  - Automatic connection management with retry logic
  - DPT 9001 temperature encoding/decoding
  - Error handling and circuit breaker pattern

### 4. Service Layer
- **Purpose**: Business logic layer between API and Modbus
- **Location**: `src/services/`
- **Components**:
  - `ZoneService`: Zone temperature and state management
  - `OperationService`: Global operation mode and state
  - `DeviceService`: Dehumidifiers, pumps, mixed groups
  - `TemperatureService`: Outside temperature readings
  - `NotificationService`: System alerts and warnings

## Data Flow Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   External      │ ──────────────► │   Flask API     │
│   Clients       │                 │   Server        │
└─────────────────┘                 └─────────────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │  Service Layer  │
                                   │  (Business      │
                                   │   Logic)        │
                                   └─────────────────┘
                                            │
                                            ▼
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     ▼
            ┌─────────────────┐                 ┌─────────────────┐
            │  Modbus Server │                 │  Modbus Client │
            │  (Data Store)  │                 │  (Physical      │
            │                │                 │   Device)       │
            └─────────────────┘                 └─────────────────┘
                    │                                     │
                    ▼                                     ▼
            ┌─────────────────┐                 ┌─────────────────┐
            │   SQLite DB     │                 │  Waveshare     │
            │  (Persistent   │                 │  Gateway       │
            │   Storage)     │                 │  (RS485-TCP)   │
            └─────────────────┘                 └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │  Physical       │
                                                │  Neasmart       │
                                                │  Device         │
                                                └─────────────────┘
```

## API Endpoints and Modbus Integration

### Zone Management (`/api/zones`)

**Read Operations:**
- API endpoint reads from Modbus server context
- Data is retrieved from SQLite database via persistent data block
- Real-time temperature, humidity, and state information

**Write Operations:**
- API writes to both Modbus server (for immediate response) and Modbus client (for physical device)
- Zone setpoints are encoded using DPT 9001 format
- Physical device receives commands through Waveshare gateway

```python
# Example: Zone setpoint update
def update_zone_data(self, base_id: int, zone_id: int, request: ZoneRequest):
    # 1. Write to Modbus server (immediate API response)
    self.context[self.slave_id].setValues(
        const.WRITE_HR_CODE,
        zone_addr,
        request.state
    )
    
    # 2. Write to physical device via Modbus client
    success, dpt_value, message = await modbus_client.write_zone_setpoint(
        base_id, zone_id, dpt_9001_setpoint
    )
```

### Operation Mode Management (`/api/mode`)

**Global System Control:**
- Operation mode (Auto, Heating, Cooling, Manual)
- Operation state (Normal, Reduced, Standby, Scheduled, Party, Holiday)
- Direct Modbus register manipulation for system-wide control

### Device Management (`/api/devices`)

**Device Types:**
- **Dehumidifiers** (`/api/dehumidifiers/{id}`): Up to 9 dehumidifiers
- **Pumps** (`/api/pumps/{id}`): Up to 5 extra pumps  
- **Mixed Groups** (`/api/mixedgroups/{id}`): Up to 3 mixed circuit groups

**Data Sources:**
- All device data read from Modbus server context
- Real-time status, temperature, and operational data
- Thread-safe access to persistent SQLite storage

### Temperature Monitoring (`/api/outsidetemperature`)

**Temperature Sources:**
- Outside temperature (raw and filtered)
- Zone-specific temperature readings
- Real-time data from Modbus registers

## Modbus Server Implementation

### Persistent Data Storage

The Modbus server uses a custom `LockingPersistentDataBlock` that provides:

```python
class LockingPersistentDataBlock(ModbusSequentialDataBlock):
    """Thread-safe Modbus data block with SQLite persistence."""
    
    def setValues(self, address, value):
        """Set values with thread safety and persistence."""
        with self.lock:
            # Log to monitor for debugging
            monitor.log_write(slave_id=0, address=address, values=value, source="external")
            
            # Update SQLite database
            for k in range(0, len(value)):
                self.reg_dict[address + k] = value[k]
            
            # Update in-memory data block
            super().setValues(address, value)
```

### Server Configuration

**TCP Server:**
```python
# Start TCP server
await StartAsyncTcpServer(
    context=server_context,
    identity=identity,
    address=(host, port),
    framer="socket",
    ignore_missing_slaves=True,
    broadcast_enable=True,
)
```

**Serial Server:**
```python
# Start Serial server (RTU over RS-485)
await StartAsyncSerialServer(
    context=server_context,
    identity=identity,
    port=serial_port,
    framer="rtu",
    stopbits=1,
    bytesize=8,
    parity="N",
    ignore_missing_slaves=True,
    broadcast_enable=True,
)
```

## Modbus Client Implementation

### Physical Device Communication

The Modbus client connects to the Waveshare RS485-to-TCP gateway to communicate with the physical Neasmart device:

```python
class NeasmartModbusClient:
    """Modbus TCP client for communicating with physical Neasmart device."""
    
    async def write_zone_setpoint(self, base_id: int, zone_id: int, 
                                  dpt_9001_value: int) -> Tuple[bool, str]:
        """Write setpoint to physical device."""
        if not await self.connect():
            return False, "Failed to connect to gateway"
        
        # Calculate register address
        zone_addr = (base_id - 1) * const.ZONE_BASE_ID_MULTIPLIER + \
                   zone_id * const.ZONE_ID_MULTIPLIER + \
                   const.ZONE_SETPOINT_ADDR_OFFSET
        
        # Write to physical device
        result = await self.client.write_register(
            address=zone_addr,
            value=dpt_9001_value,
            slave=self.neasmart_slave_id
        )
        
        return result.isError() == False, "Success" if not result.isError() else str(result)
```

### Connection Management

**Automatic Reconnection:**
- Connection pooling with automatic retry logic
- Circuit breaker pattern for error handling
- Configurable timeout and retry parameters

**Error Handling:**
```python
def _record_error(self, error_msg: str):
    """Record consecutive errors for circuit breaker."""
    self.consecutive_errors += 1
    self.last_error_time = time.time()
    _logger.error(f"Modbus client error: {error_msg} (consecutive: {self.consecutive_errors})")
```

## Configuration and Setup

### Gateway Configuration

**File**: `config/gateway.json`
```json
{
  "gateway": {
    "host": "192.168.1.100",
    "port": 502,
    "neasmart_slave_id": 240
  }
}
```

### Server Configuration

**File**: `config/server.json`
```json
{
  "server_type": "tcp",
  "listen_address": "0.0.0.0",
  "listen_port": 502,
  "slave_id": 0
}
```

### Database Configuration

**File**: `config/database.json`
```json
{
  "datastore_path": "./data/registers.db",
  "regs_table": "holding_registers"
}
```

## Register Mapping

### Zone Registers
- **Base 1, Zone 1**: Address 100 (setpoint), 101 (temperature), 109 (humidity)
- **Base 1, Zone 2**: Address 200 (setpoint), 201 (temperature), 209 (humidity)
- **Base 2, Zone 1**: Address 1300 (setpoint), 1301 (temperature), 1309 (humidity)

### Global Registers
- **Operation Mode**: Address 1
- **Operation State**: Address 2
- **Outside Temperature**: Address 7
- **Filtered Outside Temperature**: Address 8

### Mixed Circuit Groups
- **Group 1**: Base address 10
- **Group 2**: Base address 14  
- **Group 3**: Base address 18

## Monitoring and Logging

### Modbus Operation Monitor

The system includes comprehensive monitoring of all Modbus operations:

```python
class ModbusOperationLog:
    """Log entry for Modbus operations."""
    def __init__(self, source: str, slave_id: int, address: int, 
                 count: int, values: list = None):
        self.timestamp = time.time()
        self.source = source  # "api", "external", "client"
        self.slave_id = slave_id
        self.address = address
        self.count = count
        self.values = values
```

### Log Sources
- **"api"**: Operations initiated by REST API calls
- **"external"**: Operations from external Modbus clients
- **"client"**: Operations to physical device via Modbus client

## Error Handling and Recovery

### API Error Handling
- Input validation at service layer
- Graceful error responses with appropriate HTTP status codes
- Detailed error logging for debugging

### Modbus Error Handling
- Connection retry logic with exponential backoff
- Circuit breaker pattern for persistent connection failures
- Automatic reconnection on connection loss

### Data Consistency
- Thread-safe operations using locks
- Atomic database transactions
- Real-time synchronization between server and client

## Performance Considerations

### Thread Safety
- All Modbus operations are thread-safe using locks
- SQLite database with proper transaction handling
- Async operations for non-blocking I/O

### Connection Pooling
- Single Modbus client instance with connection reuse
- Automatic connection management
- Configurable timeout and retry parameters

### Data Persistence
- SQLite database for register persistence
- Automatic database initialization
- Backup and recovery mechanisms

## Security Considerations

### Network Security
- Configurable listen addresses and ports
- Optional authentication for Modbus clients
- Network isolation for production deployments

### Data Validation
- Input validation at API layer
- Register address bounds checking
- Data type validation for all operations

This architecture provides a robust, scalable solution for integrating the Rehau Neasmart 2.0 system with modern web APIs while maintaining real-time communication with the physical device.
