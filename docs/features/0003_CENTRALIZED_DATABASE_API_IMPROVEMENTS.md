# Centralized Database API Improvements Plan

## Executive Summary

This plan implements a centralized database architecture where SQLite serves as the single source of truth for all Modbus register data. The database acts as a hub between the REST API and the physical Modbus device, providing:

1. **Unified Data Access**: RegisterManager provides a high-level interface for all register operations
2. **Performance Optimization**: TTL-based caching reduces database reads
3. **Data Transformation**: Automatic conversion between raw registers, domain models, and API responses
4. **State Enrichment**: Integer states/modes automatically converted to human-readable strings
5. **Synchronization**: Bidirectional sync between local database and physical Neasmart device
6. **Consistency**: All API responses follow OpenAPI schema with camelCase fields

**Key Architecture Change**:
```
BEFORE: API → Modbus Context → Physical Device
AFTER:  API → Service → RegisterManager → Database ⇄ Physical Device
```

## Overview

This plan outlines the implementation of a centralized database approach for API responses, where the database serves as the central hub for both reading and writing Modbus data. The goal is to create a unified data layer that handles data transformation between backend (snake_case) and frontend (camelCase) formats, while providing a consistent interface for both Modbus client and REST API operations.

## Current State Analysis

### Existing Architecture
The current system has:
- Direct Modbus communication in API endpoints (`src/api/*.py`)
- Database persistence layer with SQLite (`src/database.py`, `src/modbus_server.py`) 
- Data transformation utilities (`src/utils/data_transformer.py`)
- Services that directly interact with Modbus context (`src/services/*.py`)
- DPT 9001 encoding/decoding for temperature values (`src/dpt_9001.py`)

### Current Data Models
**Zone Models** (`src/models/zone_models.py`):
- `ZoneData`: state (int 0-6), setpoint (float), temperature (float), relative_humidity (int)
- `ZoneRequest`: state (Optional[int]), setpoint (Optional[float])

**Operation Models** (`src/models/operation_models.py`):
- `OperationMode`: mode (int 1-5) - Auto, Heating, Cooling, Manual Heating, Manual Cooling
- `OperationState`: state (int 1-6) - Normal, Reduced, Standby, Scheduled, Party, Holiday

**Device Models** (`src/models/device_models.py`):
- `DehumidifierData`: state (int)
- `PumpData`: state (int)
- `MixedGroupData`: pump_state, mixing_valve_opening_percentage, flow_temperature, return_temperature

**Response Models** (`src/models/response_models.py`):
- `TemperatureData`: outside_temperature, filtered_outside_temperature
- `NotificationData`: hints_present, warnings_present, error_present
- `ErrorResponse`: error, status

### Current State Mappings
**Operation States** (from `src/const.py`):
- 0: "off"
- 1: "presence"
- 2: "away"
- 3: "standby"
- 4: "scheduled"
- 5: "party"
- 6: "holiday"

**Operation Modes** (from `src/const.py`):
- 0: "off"
- 1: "auto"
- 2: "heating"
- 3: "cooling"
- 4: "manual heating"
- 5: "manual cooling"

### Current Database Structure
- SQLite database with `holding_registers` table
- 65536 registers (address 0-65535) stored as key-value pairs
- Thread-safe operations with `LockingPersistentDataBlock`
- Autocommit enabled for immediate persistence
- Registers store raw integer values (DPT 9001 encoded for temperatures)

## Technical Requirements

### Phase 1: Enhanced Database Layer with Centralized Access

**New files to create:**
- `src/database/register_manager.py` - Centralized register management interface
- `src/database/data_cache.py` - Caching layer for improved performance
- `src/database/__init__.py` - Database package initialization

**Files to modify:**
- `src/database.py` - Move to `src/database/persistent_datablock.py` and enhance
- `src/modbus_server.py` - Update to use new database layer
- `src/const.py` - Add new constants for database operations

**Key changes:**

1. **Create RegisterManager class** - Centralized interface for register operations:
   - `read_register(address: int) -> int` - Read single register
   - `read_registers(address: int, count: int) -> List[int]` - Read multiple registers
   - `write_register(address: int, value: int) -> bool` - Write single register
   - `write_registers(address: int, values: List[int]) -> bool` - Write multiple registers
   - `read_zone_data(base_id: int, zone_id: int) -> Dict` - Read complete zone data
   - `write_zone_state(base_id: int, zone_id: int, state: int) -> bool` - Write zone state
   - `write_zone_setpoint(base_id: int, zone_id: int, setpoint: float) -> bool` - Write zone setpoint with DPT 9001 encoding
   - `read_operation_state() -> int` - Read global operation state
   - `write_operation_state(state: int) -> bool` - Write global operation state
   - `read_operation_mode() -> int` - Read global operation mode
   - `write_operation_mode(mode: int) -> bool` - Write global operation mode

2. **Implement DataCache class** - In-memory caching for frequently accessed registers:
   - TTL-based cache expiration (configurable per register type)
   - Automatic cache invalidation on write operations
   - Cache hit/miss statistics for monitoring

3. **Add database event hooks**:
   - Pre-write validation hooks
   - Post-write notification hooks for external systems
   - Change tracking for audit log

4. **Enhance LockingPersistentDataBlock**:
   - Add metadata tracking (last_modified timestamp, source)
   - Implement batch operations for multiple register writes
   - Add transaction support for atomic multi-register updates

### Phase 2: Data Transformation & Conversion Layer

**Files to create:**
- `src/utils/register_converter.py` - Convert between database registers and domain models
- `src/utils/state_converter.py` - Convert between integer states and string representations

**Files to modify:**
- `src/utils/data_transformer.py` - Enhance existing transformation utilities

**Key changes:**

1. **Create RegisterConverter class** - Convert raw register values to typed data:
   - `register_to_zone_data(registers: List[int], base_id: int, zone_id: int) -> ZoneData` - Convert registers to ZoneData model
   - `register_to_temperature(register: int) -> float` - Decode DPT 9001 temperature
   - `temperature_to_register(temp: float) -> int` - Encode temperature to DPT 9001
   - `register_to_state(register: int, state_type: str) -> str` - Convert state integer to string name
   - `state_to_register(state: str, state_type: str) -> int` - Convert state string to integer
   - `registers_to_mixed_group(registers: List[int], group_id: int) -> MixedGroupData` - Convert to MixedGroupData

2. **Create StateConverter class** - Bidirectional state conversion:
   - `operation_state_to_string(state: int) -> str` - Convert operation state int to string (e.g., 1 → "presence")
   - `string_to_operation_state(state: str) -> int` - Convert string to operation state int (e.g., "presence" → 1)
   - `operation_mode_to_string(mode: int) -> str` - Convert operation mode int to string (e.g., 2 → "heating")
   - `string_to_operation_mode(mode: str) -> int` - Convert string to operation mode int (e.g., "heating" → 2)
   - `zone_state_to_string(state: int) -> str` - Convert zone state to string
   - `string_to_zone_state(state: str) -> int` - Convert string to zone state
   - Validation for all conversions with proper error messages

3. **Enhance DataTransformer** - Improve existing utilities:
   - Add support for nested object transformation
   - Add configuration for selective field transformation
   - Implement transformation profiles (e.g., "api_response", "database_write")
   - Add type preservation for numeric fields

4. **Add comprehensive validation**:
   - Range validation for all state/mode integers
   - DPT 9001 range validation for temperatures
   - Field type validation before transformation
   - Custom validation rules per field type

### Phase 3: Service Layer Refactoring

**Files to modify:**
- `src/services/zone_service.py` - Refactor to use RegisterManager instead of Modbus context
- `src/services/operation_service.py` - Create new service for operation mode/state
- `src/services/temperature_service.py` - Modify for centralized database access
- `src/services/device_service.py` - Update device operations to use RegisterManager
- `src/services/health_service.py` - Enhance health checks for new database layer

**Key changes:**

1. **Refactor ZoneService** - Remove direct Modbus context dependency:
   - Constructor: `__init__(self, register_manager: RegisterManager)`
   - `get_zone_data(base_id, zone_id)` → Use `register_manager.read_zone_data()`
   - `update_zone_data(base_id, zone_id, request)` → Use `register_manager.write_zone_state()` and `register_manager.write_zone_setpoint()`
   - Remove write-through logic to physical device (handled by RegisterManager)
   - Add retry logic for transient database errors
   - Return enriched response with state/mode string names

2. **Create OperationService** - Centralized operation management:
   - `get_operation_state() -> OperationState` - Read state from database
   - `set_operation_state(state: int) -> bool` - Write state to database
   - `get_operation_mode() -> OperationMode` - Read mode from database
   - `set_operation_mode(mode: int) -> bool` - Write mode to database
   - Validate state/mode values before writing
   - Use StateConverter for int ↔ string conversions

3. **Refactor TemperatureService** - Simplified database access:
   - Use `register_manager.read_register(OUTSIDE_TEMPERATURE_ADDR)`
   - Use `register_manager.read_register(FILTERED_OUTSIDE_TEMPERATURE_ADDR)`
   - Apply DPT 9001 decoding via RegisterConverter
   - Add caching for temperature reads (update every 30 seconds)

4. **Refactor DeviceService** - Unified device access:
   - Use RegisterManager for all device reads
   - Implement consistent error handling
   - Add device state validation
   - Support batch device reads for performance

5. **Update HealthService** - Enhanced health monitoring:
   - Check database connectivity (RegisterManager health)
   - Check cache statistics (hit rate, size)
   - Monitor register write/read latency
   - Report Modbus client connection status
   - Include database file size and last backup timestamp

### Phase 4: API Endpoint Updates with Consistent Response Format

**Files to modify:**
- `src/api/zones.py` - Update zone endpoints with new response format
- `src/api/operation.py` - Modify operation endpoints with enriched data
- `src/api/temperature.py` - Update temperature endpoints
- `src/api/devices.py` - Modify device endpoints
- `src/api/health.py` - Update health check for database status
- `src/api/middleware.py` - Add response transformation middleware

**Key changes:**

1. **Update Zones API** (`/zones/{base_id}/{zone_id}`):
   - **GET Response** - Enriched zone data matching OpenAPI spec:
     ```json
     {
       "base": {"id": 1, "label": "First Floor"},
       "zone": {"id": 1, "label": "Living Room"},
       "state": "presence",
       "temperature": {"value": 21.5, "unit": "°C"},
       "setpoint": {"value": 22.0, "unit": "°C"},
       "relativeHumidity": 45,
       "address": 1300
     }
     ```
   - **POST Request** - Accept both state strings and integers:
     ```json
     {
       "state": "presence",  // or integer 1
       "setpoint": 22.5
     }
     ```
   - **POST Response** - Confirmation with updated values:
     ```json
     {
       "base": {"id": 1, "label": "First Floor"},
       "zone": {"id": 1, "label": "Living Room"},
       "updated": {
         "state": "presence",
         "setpoint": 22.5
       }
     }
     ```

2. **Update Operation API** (`/operation/state`, `/operation/mode`):
   - **GET /operation/state** - Return enriched state data:
     ```json
     {
       "state": "normal"
     }
     ```
   - **POST /operation/state** - Accept state name or integer:
     ```json
     {
       "state": "normal"  // or integer 1
     }
     ```
   - **POST Response**:
     ```json
     {
       "status": "success",
       "state": "normal"
     }
     ```
   - Same pattern for `/operation/mode` with mode values

3. **Update Temperature API** (`/outsidetemperature`):
   - No Modbus context access, use TemperatureService only
   - Consistent error responses
   - Add caching headers (Cache-Control: max-age=30)

4. **Update Devices API** (`/dehumidifiers/{id}`, `/pumps/{id}`):
   - Use DeviceService for all operations
   - Consistent response format
   - Add device validation

5. **Update Health API** (`/health`):
   - Enhanced response matching OpenAPI HealthResponse schema:
     ```json
     {
       "status": "healthy",
       "version": "2.1.0",
       "database": {
         "healthy": true,
         "type": "SQLite",
         "details": "Connected"
       },
       "modbus": {
         "healthy": true,
         "circuit_breaker": {
           "state": "closed",
           "failures": 0
         }
       },
       "configuration": {
         "server_type": "tcp",
         "api_auth_enabled": false,
         "fallback_enabled": true
       }
     }
     ```

6. **Create Response Transformation Middleware**:
   - Automatic snake_case → camelCase transformation for all responses
   - Automatic enrichment of state/mode integers with string names
   - Consistent error response format
   - Add request ID for tracing

### Phase 5: Modbus Client Integration & Synchronization

**Files to modify:**
- `src/modbus_client.py` - Update client to sync with centralized database
- `src/modbus_monitor.py` - Enhance monitoring for database operations
- `src/modbus_server.py` - Update server to notify database on external writes

**Key changes:**

1. **Update NeasmartModbusClient** - Database synchronization:
   - Add `register_manager: RegisterManager` to constructor
   - **Read operations**: 
     - Read from physical device via Modbus
     - Update local database with read values
     - Return values from database (ensures consistency)
   - **Write operations**:
     - Write to local database first
     - Then attempt write to physical device
     - On physical write failure: log warning but keep local value
     - On physical write success: confirm database update
   - Add retry logic for physical device communication (3 retries with exponential backoff)
   - Implement circuit breaker pattern for device communication failures

2. **Enhance ModbusMonitor** - Track database operations:
   - Log database read/write operations with source tracking
   - Add database operation statistics (reads/writes per source)
   - Monitor cache hit rates
   - Track data synchronization events (local vs physical device)
   - Generate alerts for sync failures

3. **Update Modbus Server** - External write handling:
   - When external Modbus client writes to server:
     - Update database via RegisterManager
     - Trigger notification hooks for affected registers
     - Update cache with new values
   - Implement read-through from database on external reads
   - Add conflict resolution for simultaneous writes (local API vs external Modbus)

4. **Implement Synchronization Strategy**:
   - **Priority**: Local database is source of truth
   - **Write flow**: API → Database → Physical Device
   - **External write flow**: External Device → Modbus Server → Database
   - **Read flow**: Physical Device → Cache → Database → API
   - **Conflict resolution**: Last-write-wins with timestamp tracking
   - **Periodic sync**: Background task to sync database with physical device (every 5 minutes)

## Data Transformation Requirements

### Backend to Frontend (snake_case → camelCase)
Field transformations for API responses:
- `operation_mode` → `operationMode`
- `operation_state` → `operationState`
- `outside_temperature` → `outsideTemperature`
- `filtered_outside_temperature` → `filteredOutsideTemperature`
- `relative_humidity` → `relativeHumidity`
- `zone_id` → `zoneId`
- `base_id` → `baseId`
- `pump_state` → `pumpState`
- `flow_temperature` → `flowTemperature`
- `return_temperature` → `returnTemperature`
- `mixing_valve_opening_percentage` → `mixingValveOpeningPercentage`
- `dehumidifier_state` → `dehumidifierState`
- `hints_present` → `hintsPresent`
- `warnings_present` → `warningsPresent`
- `error_present` → `errorPresent`

### Frontend to Backend (camelCase → snake_case)
Field transformations for API requests:
- `operationMode` → `operation_mode`
- `operationState` → `operation_state`
- `outsideTemperature` → `outside_temperature`
- `filteredOutsideTemperature` → `filtered_outside_temperature`
- `relativeHumidity` → `relative_humidity`
- `zoneId` → `zone_id`
- `baseId` → `base_id`

### State/Mode Integer to String Mappings

**Operation States** (for API responses):
- Integer 0 → String "off"
- Integer 1 → String "presence"
- Integer 2 → String "away"
- Integer 3 → String "standby"
- Integer 4 → String "scheduled"
- Integer 5 → String "party"
- Integer 6 → String "holiday"

**Operation Modes** (for API responses):
- Integer 0 → String "off"
- Integer 1 → String "auto"
- Integer 2 → String "heating"
- Integer 3 → String "cooling"
- Integer 4 → String "manual_heating"
- Integer 5 → String "manual_cooling"

**Zone States** (same as Operation States):
- Uses same mapping as operation states

### Temperature Transformations

**DPT 9001 Encoding/Decoding**:
- Database stores: 16-bit integer (DPT 9001 format)
- API returns: Float with 2 decimal places and unit
- API accepts: Float (converted to DPT 9001 before storage)
- Valid range: -671088.64 to 670760.96
- Example: 21.5°C → 0x0876 (2166 in decimal) → 21.5°C

## Implementation Algorithms

### 1. Database Read Operation Flow
```
1. API endpoint receives GET request (e.g., /zones/1/3)
2. Endpoint calls service method (e.g., zone_service.get_zone_data(1, 3))
3. Service calls RegisterManager.read_zone_data(1, 3)
4. RegisterManager:
   a. Check DataCache for zone registers
   b. If cache miss: read from LockingPersistentDataBlock
   c. Update cache with read values (TTL: 10 seconds for zone data)
   d. Return raw register values
5. RegisterManager uses RegisterConverter to convert registers to ZoneData model
6. Service receives ZoneData with integer state
7. Service enriches data with StateConverter (state int → string)
8. Service returns enriched model to endpoint
9. Endpoint applies DataTransformer (snake_case → camelCase)
10. Return JSON response to client
```

### 2. Database Write Operation Flow
```
1. API endpoint receives POST request (e.g., /zones/1/3 with {"state": "normal", "setpoint": 22.5})
2. Endpoint validates and parses JSON payload
3. Endpoint calls service method (e.g., zone_service.update_zone_data(1, 3, request))
4. Service validates request data
5. Service converts state string to integer via StateConverter
6. Service calls RegisterManager.write_zone_state(1, 3, 1)
7. RegisterManager:
   a. Validate state value (range check)
   b. Calculate register address: (1-1)*1200 + 3*100 = 1300
   c. Write to LockingPersistentDataBlock (persists to SQLite)
   d. Invalidate cache for affected registers
   e. Trigger post-write hooks (for Modbus client sync)
8. Post-write hook triggers NeasmartModbusClient.sync_to_physical_device()
9. ModbusClient attempts write to physical device:
   a. If success: log confirmation
   b. If failure: log warning, database value is still updated
10. For setpoint: Service calls RegisterManager.write_zone_setpoint(1, 3, 22.5)
11. RegisterManager converts temperature to DPT 9001 via dpt_9001.pack_dpt9001()
12. Write encoded value to database
13. Service returns success response
14. Endpoint transforms response and returns to client
```

### 3. External Modbus Write Handling
```
1. External Modbus client writes to gateway Modbus server
2. LockingPersistentDataBlock.setValues() called with address and value
3. setValues():
   a. Log write operation via ModbusMonitor (source: "external")
   b. Update SQLite database via reg_dict
   c. Call super().setValues() to update in-memory values
   d. Trigger RegisterManager event hook
4. RegisterManager event hook:
   a. Invalidate cache for written address
   b. Log synchronization event
   c. Optionally notify subscribed services
5. Next API read will fetch updated value from database
```

### 4. Periodic Synchronization Algorithm
```
1. Background task runs every 5 minutes
2. For each critical register (operation state, operation mode, zone states):
   a. Read value from physical device via ModbusClient
   b. Compare with local database value
   c. If different:
      - Log discrepancy
      - Apply conflict resolution (configurable: device-wins or local-wins)
      - Update database or device based on resolution
3. Update sync statistics in ModbusMonitor
4. Generate alerts for persistent sync failures
```

### 5. Cache Management Algorithm
```
1. Cache structure:
   - Key: register address
   - Value: (register_value, timestamp, ttl)
2. On read:
   a. Check if address in cache
   b. If found and not expired: return cached value (cache hit)
   c. If not found or expired: read from database, update cache (cache miss)
3. On write:
   a. Invalidate cache entry for written address
   b. Invalidate related cache entries (e.g., zone setpoint invalidates zone data cache)
4. Cache expiration TTLs:
   - Zone data: 10 seconds
   - Temperature data: 30 seconds
   - Operation state/mode: 5 seconds
   - Device states: 15 seconds
5. Cache cleanup: Remove expired entries every 60 seconds
```

### Data Flow Architecture
```
┌─────────────┐
│  API Client │
└──────┬──────┘
       │ JSON (camelCase)
       ▼
┌─────────────┐
│  API Layer  │ (Flask endpoints)
│  + Middleware│ (auto transformation)
└──────┬──────┘
       │ Models (snake_case)
       ▼
┌─────────────┐
│Service Layer│ (Business logic)
│+ StateConv. │ (int ↔ string)
└──────┬──────┘
       │ Domain models
       ▼
┌─────────────┐
│ RegisterMgr │ (Centralized DB access)
│ + RegConv.  │ (registers ↔ models)
│ + DataCache │
└──────┬──────┘
       │ Raw registers
       ▼
┌─────────────┐
│   SQLite    │ (Persistent storage)
│  Database   │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌─────────────┐
│Modbus Server│◄────►│Modbus Client│
│  (Gateway)  │      │  (Physical) │
└─────────────┘      └─────────────┘
  External Device      Neasmart 2.0
```

## Configuration Updates

**Files to modify:**
- `config/database.json` - Add database configuration options
- `config/api.json` - Update API configuration for new data flow
- `config/features.json` - Add feature flags for centralized database

### config/database.json additions
```json
{
  "cache": {
    "enabled": true,
    "ttl": {
      "zone_data": 10,
      "temperature": 30,
      "operation": 5,
      "devices": 15
    },
    "max_entries": 1000,
    "cleanup_interval": 60
  },
  "synchronization": {
    "enabled": true,
    "interval": 300,
    "conflict_resolution": "local_wins",
    "retry_count": 3,
    "retry_backoff": 2
  },
  "persistence": {
    "path": "./data/registers.db",
    "table": "holding_registers",
    "autocommit": true,
    "backup_enabled": true,
    "backup_interval": 3600
  }
}
```

### config/features.json additions
```json
{
  "centralized_database": {
    "enabled": true,
    "register_manager": true,
    "data_cache": true,
    "state_enrichment": true
  },
  "api_enhancements": {
    "auto_transformation": true,
    "state_string_conversion": true,
    "response_middleware": true
  }
}
```

## Testing Requirements

**Files to create:**
- `tests/unit/test_register_manager.py` - Unit tests for RegisterManager
- `tests/unit/test_register_converter.py` - Unit tests for RegisterConverter
- `tests/unit/test_state_converter.py` - Unit tests for StateConverter
- `tests/unit/test_data_cache.py` - Unit tests for DataCache
- `tests/unit/test_data_transformer_enhanced.py` - Unit tests for enhanced data transformation
- `tests/integration/test_centralized_database.py` - Integration tests for database operations
- `tests/integration/test_api_database_flow.py` - End-to-end API with database tests
- `tests/integration/test_modbus_sync.py` - Modbus synchronization tests

**Test Coverage Requirements:**
1. **RegisterManager tests** - Test all register operations with mocked database
2. **Converter tests** - Test all conversion functions with edge cases
3. **Cache tests** - Test cache hit/miss, expiration, invalidation
4. **Transformation tests** - Test snake_case ↔ camelCase, state int ↔ string
5. **Integration tests** - Test complete data flow from API to database to Modbus
6. **Synchronization tests** - Test external writes, conflict resolution, periodic sync

## OpenAPI Documentation Updates

**Files to modify:**
- `src/openapi.yaml` - Update API documentation to reflect new data flow and response formats

## TODO Checklist

- [ ] Phase 1 — Enhanced Database Layer with Centralized Access
  - [ ] Create database package structure `src/database/`
  - [ ] Create `src/database/__init__.py` for package initialization
  - [ ] Move `src/database.py` to `src/database/persistent_datablock.py`
  - [ ] Create `src/database/register_manager.py` with RegisterManager class
    - [ ] Implement read_register and read_registers methods
    - [ ] Implement write_register and write_registers methods
    - [ ] Implement read_zone_data method with address calculation
    - [ ] Implement write_zone_state and write_zone_setpoint methods
    - [ ] Implement read/write operation_state and operation_mode methods
    - [ ] Add event hooks for pre-write validation and post-write notifications
  - [ ] Create `src/database/data_cache.py` with DataCache class
    - [ ] Implement TTL-based cache with configurable expiration
    - [ ] Implement cache invalidation on write operations
    - [ ] Add cache statistics tracking (hits, misses, size)
    - [ ] Implement periodic cache cleanup
  - [ ] Enhance LockingPersistentDataBlock in persistent_datablock.py
    - [ ] Add metadata tracking (timestamp, source)
    - [ ] Implement batch write operations
    - [ ] Add transaction support for atomic updates
  - [ ] Add database constants to `src/const.py`

- [ ] Phase 2 — Data Transformation & Conversion Layer
  - [ ] Create `src/utils/register_converter.py` with RegisterConverter class
    - [ ] Implement register_to_zone_data conversion
    - [ ] Implement register_to_temperature (DPT 9001 decoding)
    - [ ] Implement temperature_to_register (DPT 9001 encoding)
    - [ ] Implement register_to_state conversion
    - [ ] Implement state_to_register conversion
    - [ ] Implement registers_to_mixed_group conversion
  - [ ] Create `src/utils/state_converter.py` with StateConverter class
    - [ ] Implement operation_state_to_string conversion
    - [ ] Implement string_to_operation_state conversion
    - [ ] Implement operation_mode_to_string conversion
    - [ ] Implement string_to_operation_mode conversion
    - [ ] Implement zone_state_to_string conversion
    - [ ] Implement string_to_zone_state conversion
    - [ ] Add validation for all conversions
  - [ ] Enhance `src/utils/data_transformer.py`
    - [ ] Add support for nested object transformation
    - [ ] Add selective field transformation configuration
    - [ ] Implement transformation profiles
    - [ ] Add type preservation for numeric fields
  - [ ] Add comprehensive validation
    - [ ] Range validation for states and modes
    - [ ] DPT 9001 range validation for temperatures
    - [ ] Field type validation before transformation

- [ ] Phase 3 — Service Layer Refactoring
  - [ ] Refactor `src/services/zone_service.py`
    - [ ] Change constructor to accept RegisterManager
    - [ ] Update get_zone_data to use register_manager.read_zone_data
    - [ ] Update update_zone_data to use RegisterManager methods
    - [ ] Remove direct Modbus context dependency
    - [ ] Add retry logic for database errors
    - [ ] Add state/mode string enrichment via StateConverter
  - [ ] Create `src/services/operation_service.py`
    - [ ] Implement get_operation_state method
    - [ ] Implement set_operation_state method
    - [ ] Implement get_operation_mode method
    - [ ] Implement set_operation_mode method
    - [ ] Add state/mode validation
    - [ ] Use StateConverter for int ↔ string conversions
  - [ ] Refactor `src/services/temperature_service.py`
    - [ ] Update to use RegisterManager for register reads
    - [ ] Apply DPT 9001 decoding via RegisterConverter
    - [ ] Add caching for temperature reads (30s TTL)
  - [ ] Refactor `src/services/device_service.py`
    - [ ] Update to use RegisterManager for all device operations
    - [ ] Add consistent error handling
    - [ ] Add device state validation
    - [ ] Support batch device reads
  - [ ] Update `src/services/health_service.py`
    - [ ] Add database connectivity checks
    - [ ] Add cache statistics reporting
    - [ ] Monitor register operation latency
    - [ ] Report Modbus client connection status
    - [ ] Include database file size and backup info

- [ ] Phase 4 — API Endpoint Updates with Consistent Response Format
  - [ ] Update `src/api/zones.py`
    - [ ] Modify GET /zones/{base_id}/{zone_id} response format
    - [ ] Add base and zone label enrichment
    - [ ] Add temperature object with value and unit
    - [ ] Update POST request to accept state strings
    - [ ] Update POST response with updated fields
  - [ ] Update `src/api/operation.py`
    - [ ] Modify GET /operation/state to return state string
    - [ ] Update POST /operation/state to accept state string or int
    - [ ] Update response format with status and state
    - [ ] Same updates for /operation/mode endpoint
  - [ ] Update `src/api/temperature.py`
    - [ ] Remove Modbus context access
    - [ ] Use TemperatureService only
    - [ ] Add caching headers (Cache-Control: max-age=30)
  - [ ] Update `src/api/devices.py`
    - [ ] Use DeviceService for all operations
    - [ ] Add consistent response format
    - [ ] Add device validation
  - [ ] Update `src/api/health.py`
    - [ ] Implement enhanced HealthResponse schema
    - [ ] Add database health section
    - [ ] Add modbus health with circuit breaker info
    - [ ] Add configuration section
  - [ ] Create `src/api/middleware.py`
    - [ ] Implement automatic snake_case → camelCase transformation
    - [ ] Implement state/mode enrichment middleware
    - [ ] Add consistent error response formatting
    - [ ] Add request ID for tracing

- [ ] Phase 5 — Modbus Client Integration & Synchronization
  - [ ] Update `src/modbus_client.py`
    - [ ] Add RegisterManager to constructor
    - [ ] Update read operations to sync with database
    - [ ] Update write operations (database first, then device)
    - [ ] Add retry logic with exponential backoff (3 retries)
    - [ ] Implement circuit breaker for device failures
    - [ ] Add write failure handling (keep database value)
  - [ ] Enhance `src/modbus_monitor.py`
    - [ ] Add database operation logging with source tracking
    - [ ] Add database operation statistics
    - [ ] Monitor cache hit rates
    - [ ] Track data synchronization events
    - [ ] Generate alerts for sync failures
  - [ ] Update `src/modbus_server.py`
    - [ ] Update external write handling to use RegisterManager
    - [ ] Trigger notification hooks on external writes
    - [ ] Update cache on external writes
    - [ ] Implement conflict resolution for simultaneous writes
  - [ ] Implement periodic synchronization
    - [ ] Create background task for 5-minute sync
    - [ ] Read critical registers from physical device
    - [ ] Compare with database values
    - [ ] Apply conflict resolution policy
    - [ ] Log sync statistics and alerts

- [ ] Phase 6 — Configuration, Testing & Documentation
  - [ ] Update `config/database.json`
    - [ ] Add cache configuration (TTLs, max entries, cleanup interval)
    - [ ] Add synchronization configuration
    - [ ] Add persistence configuration with backup settings
  - [ ] Update `config/features.json`
    - [ ] Add centralized_database feature flags
    - [ ] Add api_enhancements feature flags
  - [ ] Update `config/api.json` for new data flow
  - [ ] Create `tests/unit/test_register_manager.py`
  - [ ] Create `tests/unit/test_register_converter.py`
  - [ ] Create `tests/unit/test_state_converter.py`
  - [ ] Create `tests/unit/test_data_cache.py`
  - [ ] Create `tests/unit/test_data_transformer_enhanced.py`
  - [ ] Create `tests/integration/test_centralized_database.py`
  - [ ] Create `tests/integration/test_api_database_flow.py`
  - [ ] Create `tests/integration/test_modbus_sync.py`
  - [ ] Update `src/openapi.yaml` to reflect new response formats
