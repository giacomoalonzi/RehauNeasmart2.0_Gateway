# Constants Refactoring Plan

## Overview

This plan outlines the refactoring of constants in `src/const.py` to use the new, more descriptive and well-documented constants while deprecating the old ones. The new constants provide better naming conventions, comprehensive documentation, and improved maintainability.

## Current State Analysis

The `const.py` file contains both old constants (lines 1-35) and new constants (lines 38-133). The old constants are actively used throughout the codebase in 14+ files, while the new constants are not yet utilized.

### Old Constants Usage
- `NEASMART_BASE_SLAVE_ADDR` and `BASE_ZONE_ID` used in zone address calculations
- `OUTSIDE_TEMP_REG` and `FILTERED_OUTSIDE_TEMP_REG` used in temperature services
- Various offset constants used in Modbus operations
- No state/mode mapping constants currently used

### New Constants Benefits
- Better naming conventions (e.g., `ZONE_BASE_ID_MULTIPLIER` vs `NEASMART_BASE_SLAVE_ADDR`)
- Comprehensive documentation with page references
- State and mode mapping dictionaries for API transformations
- More descriptive variable names
- Better organization and grouping

## Files Requiring Changes

### Core Service Files
- `src/services/zone_service.py` - Zone address calculations and operations
- `src/services/temperature_service.py` - Temperature register access
- `src/services/notification_service.py` - Status register access
- `src/services/device_service.py` - Device operations
- `src/modbus_client.py` - Modbus client operations
- `src/modbus_server.py` - Modbus server operations

### API Files
- `src/api/operation.py` - Operation mode/state handling
- `src/api/zones.py` - Zone API endpoints

### Application Files
- `src/app_factory.py` - Application configuration
- `src/database.py` - Database operations

### Debug/Test Files
- `debug_timing.py` - Timing debug operations
- `debug_setpoint.py` - Setpoint debug operations
- `debug_persistence.py` - Persistence debug operations

## Implementation Strategy

### Phase 1: Constants Migration and Deprecation
1. **Add deprecation warnings** to old constants
2. **Create migration mapping** between old and new constants
3. **Update core service files** to use new constants
4. **Maintain backward compatibility** during transition

### Phase 2: API Enhancement with State/Mode Mappings
1. **Implement state/mode transformations** in API responses
2. **Add data transformation utilities** for snake_case ↔ camelCase
3. **Update API endpoints** to use mapping dictionaries
4. **Enhance error handling** with better constant usage

### Phase 3: Testing and Validation
1. **Update all test files** to use new constants
2. **Add validation tests** for constant usage
3. **Verify backward compatibility** during migration
4. **Update documentation** with new constant usage

## Data Transformation Requirements

### Backend to Frontend (snake_case → camelCase)
- `operation_mode` → `operationMode`
- `operation_state` → `operationState`
- `outside_temperature` → `outsideTemperature`
- `filtered_outside_temperature` → `filteredOutsideTemperature`
- `relative_humidity` → `relativeHumidity`

### Frontend to Backend (camelCase → snake_case)
- `operationMode` → `operation_mode`
- `operationState` → `operation_state`
- `outsideTemperature` → `outside_temperature`
- `filteredOutsideTemperature` → `filtered_outside_temperature`
- `relativeHumidity` → `relative_humidity`

## Constant Migration Mapping

### Address Calculation Constants
- `NEASMART_BASE_SLAVE_ADDR` → `ZONE_BASE_ID_MULTIPLIER`
- `BASE_ZONE_ID` → `ZONE_ID_MULTIPLIER`

### Register Address Constants
- `OUTSIDE_TEMP_REG` → `OUTSIDE_TEMPERATURE_ADDR`
- `FILTERED_OUTSIDE_TEMP_REG` → `FILTERED_OUTSIDE_TEMPERATURE_ADDR`

### Modbus Function Codes
- `READ_HR_CODE` → `READ_HR_CODE` (unchanged)
- `WRITE_HR_CODE` → `WRITE_HR_CODE` (unchanged)

### New Constants to Implement
- `NEASMART_SLAVE_ADDRESS_PRIMARY` - For Modbus client connections
- `NEASMART_SLAVE_ADDRESS_SECONDARY` - For secondary device connections
- `STATE_MAPPING` and `STATE_MAPPING_REVERSE` - For API state transformations
- `MODE_MAPPING` and `MODE_MAPPING_REVERSE` - For API mode transformations

## Backward Compatibility Strategy

1. **Deprecation Warnings**: Add warnings to old constants without breaking functionality
2. **Gradual Migration**: Update files incrementally to use new constants
3. **Alias Support**: Maintain old constant names as aliases during transition period
4. **Documentation**: Update all documentation to reference new constants
5. **Testing**: Ensure all existing functionality continues to work

## TODO Checklist

- [ ] Phase 1 — Constants Migration and Deprecation
  - [ ] Add deprecation warnings to old constants in `src/const.py`
  - [ ] Create migration mapping between old and new constants
  - [ ] Update zone address calculations in `src/services/zone_service.py`
  - [ ] Update temperature register access in `src/services/temperature_service.py`
  - [ ] Update notification register access in `src/services/notification_service.py`
  - [ ] Update Modbus client operations in `src/modbus_client.py`
  - [ ] Update Modbus server operations in `src/modbus_server.py`
  - [ ] Update application configuration in `src/app_factory.py`
  - [ ] Update database operations in `src/database.py`
  - [ ] Update debug files to use new constants
  - [ ] Update test files to use new constants

- [ ] Phase 2 — API Enhancement with State/Mode Mappings
  - [ ] Implement state/mode transformations in `src/api/operation.py`
  - [ ] Add data transformation utilities for snake_case ↔ camelCase
  - [ ] Update API endpoints to use mapping dictionaries
  - [ ] Enhance error handling with better constant usage
  - [ ] Add state/mode validation using new mapping constants
  - [ ] Update API response models to use transformed data

- [ ] Phase 3 — Testing and Validation
  - [ ] Add unit tests for new constant usage in `tests/unit/`
  - [ ] Add integration tests for constant migration in `tests/integration/`
  - [ ] Verify backward compatibility during migration
  - [ ] Update API documentation with new constant usage
  - [ ] Add configuration examples for new constants
  - [ ] Validate all existing functionality continues to work
  - [ ] Remove deprecated constants after migration is complete
