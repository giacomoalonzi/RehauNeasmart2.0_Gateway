# Development Setup Guide

This guide helps you set up a development environment for the Rehau Neasmart 2.0 Gateway.

## Prerequisites

- Python 3.9 or higher (3.12+ recommended)
- Git
- Virtual environment support (`venv`)
- A Modbus simulator or access to real hardware

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-username/RehauNeasmart2.0_Gateway.git
cd RehauNeasmart2.0_Gateway
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# For development tools (testing, linting, etc.)
pip install pytest pytest-cov black flake8 mypy
```

### 4. Configure Application

```bash
# Copy example configuration
cp data/config.json.example data/config.json

# Edit with your settings
# - Update server.address with your Modbus device IP
# - Configure your zones in structures array
```

## Running the Application

### Development Mode

```bash
# From project root
cd src
python main.py
```

This runs with:

- Debug logging enabled
- Auto-reload on code changes
- Detailed error messages

### With Environment Variables

```bash
# Override configuration
export NEASMART_LOG_LEVEL=DEBUG
export NEASMART_DEBUG_MODE=true
cd src && python main.py
```

### Using VS Code

1. Open the project folder in VS Code
2. Select the Python interpreter from your virtual environment
3. Use F5 to run with debugging

Example `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Gateway",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/src/main.py",
      "console": "integratedTerminal",
      "env": {
        "NEASMART_LOG_LEVEL": "DEBUG",
        "NEASMART_DEBUG_MODE": "true"
      }
    }
  ]
}
```

## Testing

### Run All Tests

```bash
# From project root
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ -v --cov=src --cov-report=html --cov-report=term
# Open htmlcov/index.html to view coverage report
```

### Run Specific Tests

```bash
# Run only unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_database.py -v

# Run specific test
pytest tests/unit/test_database.py::test_database_init -v
```

### Writing Tests

Create test files in `tests/` following the pattern `test_*.py`:

```python
import pytest
from src.database import DatabaseManager

def test_database_connection():
    """Test database connection"""
    db = DatabaseManager(":memory:")
    assert db.is_healthy()

@pytest.fixture
def mock_modbus():
    """Fixture for mocking Modbus"""
    # Setup mock
    yield mock
    # Teardown
```

## Code Quality

### Formatting

```bash
# Format all code
black src/ tests/

# Check formatting
black src/ tests/ --check
```

### Linting

```bash
# Run flake8
flake8 src/ tests/ --max-line-length=100

# Run with specific ignores
flake8 src/ --ignore=E501,W503
```

### Type Checking

```bash
# Run mypy
mypy src/ --ignore-missing-imports
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/sh
black src/ tests/ --check
flake8 src/ tests/
pytest tests/unit/ -q
```

## Debugging

### Enable Debug Logging

```python
# In your code
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message with %s", variable)
```

### Using pdb

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or in Python 3.7+
breakpoint()
```

### Modbus Debugging

```bash
# Enable Modbus debug logs
export NEASMART_LOG_LEVEL=DEBUG
export PYTHONUNBUFFERED=1
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following PEP 8
- Add docstrings to all functions
- Update tests for new functionality

### 3. Test Your Changes

```bash
# Run tests
pytest tests/ -v

# Check code quality
black src/ --check
flake8 src/
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature

- Detailed description
- Breaking changes (if any)
- Issue references"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

## Project Structure

```
RehauNeasmart2.0_Gateway/
├── src/                    # Source code
│   ├── api/               # API endpoints
│   ├── main.py            # Application entry point
│   ├── config.py          # Configuration management
│   ├── database.py        # Database layer
│   └── modbus_manager.py  # Modbus communication
├── tests/                  # Test files
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                   # Documentation
├── data/                   # Runtime data
│   ├── config.json        # Configuration
│   └── registers.db       # Database
└── requirements.txt        # Dependencies
```

## Common Development Tasks

### Adding a New API Endpoint

1. Create route in `src/api/your_module.py`
2. Register blueprint in `src/main.py`
3. Add tests in `tests/unit/test_your_module.py`
4. Update API documentation

### Adding Configuration Option

1. Update dataclass in `src/config.py`
2. Add default value
3. Add environment variable mapping
4. Update documentation

### Modifying Database Schema

1. Update schema in `src/database.py`
2. Add migration logic if needed
3. Update tests
4. Document changes

## Troubleshooting Development Issues

### Import Errors

```bash
# Ensure you're in virtual environment
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Lock Errors

```bash
# Remove database file
rm data/registers.db

# Application will recreate it
```

### Port Already in Use

```bash
# Find process using port
lsof -i :5001

# Kill it
kill -9 <PID>
```

## Performance Testing

### Using locust

```bash
pip install locust

# Create locustfile.py
# Run load test
locust -f locustfile.py --host=http://localhost:5001
```

### Memory Profiling

```bash
pip install memory_profiler

# Add @profile decorator
# Run with profiler
python -m memory_profiler src/main.py
```

## Contributing Guidelines

1. Follow PEP 8 style guide
2. Write descriptive commit messages
3. Add tests for new features
4. Update documentation
5. Ensure all tests pass
6. Keep PRs focused and small

## Useful Resources

- [Python Style Guide](https://pep8.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Modbus Protocol](https://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf)
- [Flask Best Practices](https://flask.palletsprojects.com/en/2.3.x/patterns/)
