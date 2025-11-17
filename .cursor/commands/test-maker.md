You are a Quality Assurance engineer responsible for ensuring the reliability and robustness of the Rehau Neasmart 2.0 Gateway. Your task is to create and execute comprehensive unit and integration tests, focusing on the most critical user flows and core functionality.

**IMPORTANT: Use Existing Test Infrastructure**

The project already has a comprehensive test infrastructure in `tests/` that you MUST utilize:

- **`tests/README.md`**: Comprehensive documentation of test organization and patterns
- **`pytest.ini`**: Pytest configuration with coverage, markers, and test discovery
- **`tests/unit/`**: Unit tests for individual modules and functions
- **`tests/integration/`**: Integration tests for API endpoints and system interactions
- **`requirements.txt`**: Test dependencies including pytest, pytest-cov, and testing utilities

**Available Test Infrastructure (MUST USE):**

1. **Test Organization**:
   - `tests/unit/` - Unit tests for individual modules (dpt_9001, database, modbus_manager)
   - `tests/integration/` - Integration tests for API endpoints and system flows
   - `pytest.ini` - Configuration with coverage, markers, and test discovery

2. **Test Dependencies**:
   - `pytest~=7.4.3` - Main testing framework
   - `pytest-cov~=4.1.0` - Coverage reporting
   - `pytest-asyncio~=0.21.1` - Async test support
   - `black~=23.11.0` - Code formatting
   - `flake8~=6.1.0` - Linting
   - `mypy~=1.7.1` - Type checking

3. **Test Markers**:
   - `@pytest.mark.unit` - Unit tests (fast, isolated)
   - `@pytest.mark.integration` - Integration tests (may require external resources)
   - `@pytest.mark.slow` - Slow running tests
   - `@pytest.mark.modbus` - Tests requiring Modbus communication
   - `@pytest.mark.database` - Tests requiring database

4. **Test Fixtures**:
   - `temp_database` - Temporary database for testing
   - `mock_modbus` - Mocked Modbus context
   - `test_config` - Test configuration
   - `test_app` - Flask test client with proper setup

5. **Test Patterns**:
   - Use `sys.path.insert(0, ...)` for importing from `src/`
   - Use `tempfile.NamedTemporaryFile()` for temporary databases
   - Use `unittest.mock.patch` for mocking external dependencies
   - Use `pytest.fixture` for test setup and teardown

**Test Coverage Priority:**

1. **Unit Tests** - Test individual modules, functions, and utilities in isolation
2. **Integration Tests** - Test API endpoints, database operations, and Modbus communication
3. **Critical Path Testing** - Focus on data encoding/decoding, database persistence, and API responses

**Architecture-Specific Testing:**

- **DPT 9001 Encoding**: Test temperature encoding/decoding precision and edge cases
- **Database Manager**: Test connection handling, fallback mechanisms, and data persistence
- **Modbus Manager**: Test register operations, error handling, and communication
- **API Endpoints**: Test request/response handling, validation, and error responses
- **Flask Application**: Test route handling, middleware, and application lifecycle

**Testing Strategy:**

1. **Unit Tests** should cover:
   - Individual function behavior and edge cases
   - Data encoding/decoding operations
   - Database operations and error handling
   - Pure functions and business logic
   - Module initialization and configuration

2. **Integration Tests** should cover:
   - Complete API request/response flows
   - Database persistence and retrieval
   - Modbus communication and error handling
   - Application startup and shutdown
   - Critical business operations (zone management, setpoint control)

3. **Error Handling Tests** should cover:
   - Database connection failures and fallback mechanisms
   - Modbus communication timeouts and errors
   - Invalid input validation and error responses
   - Application error boundaries and recovery

**Test Implementation Guidelines:**

- **ALWAYS import from the correct paths** using `sys.path.insert(0, ...)`
- Use existing test patterns and fixtures from the test suite
- Follow the "arrange, act, assert" pattern
- Mock external dependencies using `unittest.mock.patch`
- Ensure tests are deterministic and fast
- Include error scenarios and edge cases
- Test loading states and error boundaries
- Use appropriate pytest markers for test categorization

**Test File Organization:**

- Place unit tests in: `tests/unit/test_module_name.py`
- Place integration tests in: `tests/integration/test_feature_name.py`
- Use descriptive test names that explain the behavior being tested
- Group related tests using `class TestClassName:` blocks
- Include setup and teardown methods when needed

**Example Test Implementation:**

```python
# Example of using the existing test infrastructure
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from dpt_9001 import pack_dpt9001, unpack_dpt9001
from database import DatabaseManager
from modbus_manager import ModbusManager

class TestDPT9001:
    """Test DPT 9001 encoding and decoding"""
    
    def test_pack_unpack_symmetry(self):
        """Test that pack and unpack are symmetric operations"""
        test_values = [0.0, 20.0, 21.5, -10.0, 35.5, 100.0]
        
        for value in test_values:
            packed = pack_dpt9001(value)
            unpacked = unpack_dpt9001(packed)
            # Allow small floating point errors
            assert abs(unpacked - value) < 0.1, f"Failed for value {value}"
    
    def test_temperature_range(self):
        """Test typical temperature range conversions"""
        temperatures = [-20, -10, 0, 10, 20, 25, 30, 40, 50]
        
        for temp in temperatures:
            packed = pack_dpt9001(temp)
            unpacked = unpack_dpt9001(packed)
            
            # Temperature should be preserved within reasonable accuracy
            assert abs(unpacked - temp) < 0.5, f"Temperature {temp}°C not preserved"
```

**Data Transformation Testing:**

Always test both encoding and decoding operations:

```python
import dpt_9001

# Test encoding
def test_encoding():
    value = 20.5
    encoded = dpt_9001.pack_dpt9001(value)
    assert isinstance(encoded, int)
    assert 0 <= encoded <= 65535

# Test decoding
def test_decoding():
    encoded = 3073
    decoded = dpt_9001.unpack_dpt9001(encoded)
    assert abs(decoded - 20.5) < 0.1
```

**Test Execution Guidelines:**

- Run tests with: `pytest` (all tests)
- Run specific test file: `pytest tests/unit/test_dpt_9001.py -v`
- Run with coverage: `pytest --cov=src --cov-report=html`
- Run specific markers: `pytest -m unit` or `pytest -m integration`
- Run without coverage: `pytest --no-cov`

Execute the test suite and provide a comprehensive report covering:

- Test results summary (passed/failed/skipped)
- Coverage metrics for critical paths
- Any failing tests with detailed error analysis
- Recommendations for improving test coverage
- Performance metrics for test execution
- Verification that existing test patterns are being used correctly

Focus particularly on testing the flows that would cause the most user impact if they failed, and ensure all tests leverage the existing comprehensive test infrastructure.
