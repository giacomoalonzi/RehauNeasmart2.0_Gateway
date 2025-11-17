## 2.0.0

#### Added:

- **Architectural Refactoring**: Complete restructuring from monolithic `main.py` (448 lines) to modular architecture with separation of concerns
  - Created Flask application factory pattern (`app_factory.py`)
  - Separated API layer into blueprints (`api/` directory with 8 endpoint modules)
  - Extracted business logic into service layer (`services/` directory)
  - Introduced data models layer (`models/` directory)
  - Reduced main file complexity by 89% (from 448 to ~50 lines)

- **OpenAPI Documentation**: Comprehensive API documentation system
  - Automatic OpenAPI 3.0 specification generation from Flask routes
  - Interactive Swagger UI available at `/api/docs`
  - OpenAPI YAML endpoint at `/api/openapi.yaml`
  - OpenAPI JSON endpoint at `/api/openapi.json`
  - Complete API schema documentation with request/response examples

- **Data Transformation Layer**: Automatic data format conversion
  - Backend uses snake_case, frontend uses camelCase
  - Automatic transformation utilities (`utils/data_transformer.py`)
  - Bidirectional conversion for API requests and responses
  - Field mapping support for selective transformations

- **State/Mode Conversion**: Human-readable state and mode values
  - New `utils/state_converter.py` for bidirectional integer ↔ string conversion
  - Operation states: `off`, `presence`, `away`, `standby`, `scheduled`, `party`, `holiday`
  - Operation modes: `auto`, `heating`, `cooling`, `manual_heating`, `manual_cooling`
  - Zone states: `off`, `presence`, `away`, `standby`, `scheduled`
  - API endpoints support human-readable string values for states and modes

- **Enhanced Configuration Management**: Improved configuration system
  - Centralized configuration loading (`config.py`)
  - Support for JSON-based configuration files in `config/` directory
  - Environment variable overrides
  - Configuration validation and error handling

- **Service Layer**: Business logic abstraction
  - `zone_service.py`: Zone data management and validation
  - `operation_service.py`: Operation mode/state management
  - `temperature_service.py`: Temperature data processing
  - `device_service.py`: Device state management
  - `notification_service.py`: Notification status handling
  - `health_service.py`: Enhanced health checks with detailed status

- **Data Models**: Type-safe data structures
  - `zone_models.py`: Zone data structures with validation
  - `operation_models.py`: Operation mode/state models with string support
  - `device_models.py`: Device data structures
  - `response_models.py`: Standardized API response structures
  - Pydantic-based validation for all models

- **Constants Refactoring**: Improved constant management
  - Deprecated old constants with migration warnings
  - New descriptive constant names (e.g., `ZONE_BASE_ID_MULTIPLIER`, `OUTSIDE_TEMPERATURE_ADDR`)
  - State and mode mapping dictionaries (`STATE_MAPPING`, `MODE_MAPPING`)
  - Backward compatibility maintained during transition period

- **Enhanced Error Handling**: Comprehensive error management
  - Standardized error response format
  - Detailed error messages with context
  - Proper HTTP status codes
  - Error logging and tracking

- **Testing Infrastructure**: Improved test coverage
  - Unit tests for state conversion utilities
  - Integration tests for API endpoints
  - Mock Modbus context for deterministic testing
  - Test fixtures and utilities

#### Changed:

- **Database Architecture**: Enhanced database layer
  - Improved `LockingPersistentDataBlock` with better thread safety
  - Enhanced SQLite persistence with metadata tracking
  - Better error handling and recovery mechanisms

- **Modbus Communication**: Improved Modbus integration
  - Better error handling in Modbus client
  - Enhanced circuit breaker patterns
  - Improved connection management

- **API Response Format**: Standardized response structure
  - Consistent camelCase field naming in API responses
  - Enriched responses with human-readable state/mode values
  - Improved error response format

- **Code Organization**: Better project structure
  - Clear separation between API, services, models, and utilities
  - Improved code maintainability and testability
  - Better import organization

#### Removed:

- **Monolithic Structure**: Removed single-file architecture
  - Eliminated 448-line `main.py` in favor of modular structure
  - Removed direct Modbus context access from API endpoints
  - Removed mixed concerns in single files

#### Technical Details:

- **Python Version**: Compatible with Python 3.9+
- **Dependencies**: Updated requirements with new packages for OpenAPI support
- **API Base Path**: All endpoints are available under `/api/` namespace
- **Backward Compatibility**: All existing endpoints remain functional

---

## 0.2.7

#### Added:

- Extracted project version dynamically from Git tags with a fallback to v0.0.0.
- Implemented unit testing using Python's unittest framework.
- Added debug steps for version extraction and Docker login validation.

#### Changed:

- Updated GitHub Actions workflow to run unit tests before building Docker images.
- Enhanced Docker Hub authentication by using GitHub Secrets.

#### Removed:

- Removed the changelog update step from the CI/CD workflow for simplification.

## 0.2.6

- Fix POST endpoint set zone op_status temperature target, typos

## 0.2.5

- Fix POST endpoint set zone op_status temperature target

## 0.2.4

- Consolidate usage of singular v plural

## 0.2.3

- Consolidate meaning of state v status

## 0.2.2

- Remove shadowing of binary status for pumps, dehumidifiers running status

## 0.2.1

- Fix ported go -> python KNX DPT9001 pack function to accommodate for python 256 int to byte mapping

## 0.2.0

- First release of at least working addon

## 0.1.0

- Initial release
