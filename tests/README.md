# Test Suite Documentation

## Overview

This directory contains the test suite for the Rehau Neasmart 2.0 Gateway. Tests are organized into unit and integration tests.

## Running Tests

### All Tests

```bash
pytest
```

### Specific Test File

```bash
pytest tests/unit/test_dpt_9001.py -v
```

### With Coverage

```bash
pytest --cov=src --cov-report=html
```

### Without Coverage

```bash
pytest --no-cov
```

## Test Organization

```
tests/
├── unit/                    # Unit tests for individual modules
│   ├── test_dpt_9001.py     # DPT 9001 encoding/decoding tests
│   ├── test_database.py     # Database manager tests
│   └── test_config.py       # Configuration tests (TODO)
└── integration/             # Integration tests
    ├── test_api.py          # API endpoint tests (TODO)
    └── test_modbus.py       # Modbus communication tests (TODO)
```

## Writing Tests

### Unit Test Example

```python
import pytest
from src.module import function_to_test

class TestModule:
    def test_function_behavior(self):
        result = function_to_test(input_value)
        assert result == expected_value
```

### Integration Test Example

```python
import pytest
from flask import Flask
from src.main import create_app

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

def test_api_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
```

## Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
def test_integration_scenario():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

Run specific markers:

```bash
pytest -m unit
pytest -m "not slow"
```

## Fixtures

Common fixtures are available:

- `temp_database`: Temporary database for testing
- `mock_modbus`: Mocked Modbus context
- `test_config`: Test configuration

## Coverage Goals

- Unit tests: 80% coverage minimum
- Integration tests: Critical paths covered
- Edge cases: All boundary conditions tested

## CI/CD Integration

Tests run automatically on:

- Push to main branch
- Pull request creation
- Pre-commit hooks (optional)

## Debugging Tests

### Verbose Output

```bash
pytest -vv
```

### Stop on First Failure

```bash
pytest -x
```

### Debug with PDB

```bash
pytest --pdb
```

### Show Local Variables

```bash
pytest -l
```
