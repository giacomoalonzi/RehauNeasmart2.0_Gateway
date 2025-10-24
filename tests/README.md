# Test Suite for Rehau Neasmart 2.0 Gateway

This directory contains tests for the zones setpoint functionality.

## Test Structure

- `integration/` - Integration tests that test the full API flow
- `unit/` - Unit tests with mocked dependencies for faster execution

## Running Tests

### Option 1: Using the Simple Test Runner

Run the main test script from the project root:

```bash
python test_setpoint.py
```

This will give you options:
1. Full test (with 10-second wait as requested)
2. Quick test (no wait, for development)

### Option 2: Using pytest

Run all tests:
```bash
pytest
```

Run only integration tests:
```bash
pytest tests/integration/
```

Run only unit tests:
```bash
pytest tests/unit/
```

Run specific test:
```bash
pytest tests/integration/test_zones_setpoint.py::TestZonesSetpoint::test_setpoint_set_and_get
```

### Option 3: Using pytest with markers

Run only integration tests:
```bash
pytest -m integration
```

Run only unit tests:
```bash
pytest -m unit
```

## Test Description

The main test (`test_setpoint_set_and_get`) implements the exact requirement:

1. **POST** to `api/zones/1/2` with `{"setpoint": 20}`
2. **Wait 10 seconds**
3. **GET** from `api/zones/1/2`
4. **Verify** the response contains `{"setpoint": 20}`

## Test Files

- `integration/test_zones_setpoint.py` - Full integration test with 10-second wait
- `unit/test_zones_setpoint_unit.py` - Fast unit tests with mocked dependencies
- `test_setpoint.py` - Simple test runner script

## Expected Response Format

The GET request should return:
```json
{
  "state": 1,
  "setpoint": 20,
  "temperature": 22.5,
  "relativeHumidity": 45
}
```

## Dependencies

Make sure you have the required dependencies installed:
```bash
pip install pytest requests
```
