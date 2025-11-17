# Lint Fix Command

This command automatically fixes linting issues across the Rehau Neasmart 2.0 Gateway Python/Flask project using black, ruff, flake8, mypy, isort, and pytest.

## What it does

1. **Black Formatting**: Automatically formats code according to PEP 8 style guidelines
2. **Ruff Linting**: Fast Python linter that checks for errors and style issues
3. **Import Sorting**: Organizes imports with isort according to project conventions
4. **Type Checking**: Validates Python types with mypy
5. **Code Quality**: Checks for common issues with flake8
6. **Test Validation**: Runs pytest to ensure fixes don't break functionality

## Usage

Run this command when you want to:

- Fix linting errors automatically
- Format code consistently
- Clean up imports and unused code
- Ensure code follows Python/Flask project standards
- Validate type hints and catch type errors

## Commands executed

```bash
# Format code with black
black .

# Lint and auto-fix with ruff
ruff check . --fix
ruff format .

# Sort imports with isort
isort .

# Type check with mypy
mypy src/

# Lint with flake8 (read-only, no auto-fix)
flake8 src/ tests/

# Run tests to ensure fixes don't break functionality
pytest
```

## Scope

This command works on:

- **`src/`**: Main application code (Flask API, Modbus client, services, models)
- **`tests/`**: Test suite (unit and integration tests)
- **`config/`**: Configuration files (if Python files are present)

**Note**: Database files (`data/*.db`), logs, and virtual environments are excluded.

## What gets fixed

### Auto-fixes (automatic)

- **Code Style**: Indentation, spacing, line length, quotes (black)
- **Import Organization**: Alphabetical sorting, grouping (standard library → third-party → local) (isort)
- **Code Quality**: Unused imports, undefined names, syntax errors (ruff)
- **Formatting**: Consistent code formatting across the project (ruff format)

### Type Checking (mypy)

- Type errors and inconsistencies
- Missing type hints
- Incorrect type annotations
- Import type checking

### Code Quality Checks (flake8)

- PEP 8 style violations
- Complexity warnings
- Unused variables and imports
- Code smells

## Manual fixes required

Some issues require manual attention:

- Complex type errors that need architectural changes
- Logic errors or bugs
- Architecture decisions
- Custom type stubs for third-party libraries
- Flask-specific patterns that need manual review
- Modbus communication logic that requires domain knowledge

## Project-specific rules

The command respects these project conventions:

- **Python Version**: Python 3.9+
- **Code Style**: Black formatting (line length: 88 characters)
- **Import Order**: Standard library → Third-party → Local imports (isort)
- **Type Hints**: Gradual typing with mypy (strict mode recommended)
- **Flask Patterns**: Blueprint-based architecture, service layer separation
- **Modbus**: Circuit breaker patterns, error handling, retry logic
- **Testing**: pytest with markers (`@pytest.mark.unit`, `@pytest.mark.integration`)

## Dependencies

All linting tools should be installed via `requirements.txt` or development dependencies:

```bash
pip install -r requirements.txt
pip install black ruff flake8 mypy isort pytest pytest-cov
```

See `requirements.txt` for the complete list of project dependencies.

## CI Integration

Linting checks are typically integrated into CI/CD pipelines (e.g., GitHub Actions) to ensure code quality before merging:

```yaml
# Example CI step
- name: Lint and Format Check
  run: |
    black --check .
    ruff check .
    isort --check-only .
    mypy src/
    flake8 src/ tests/
```

## Output

After running, you'll see:

- ✅ Fixed issues count (black, ruff, isort)
- ⚠️ Remaining issues that need manual attention (mypy, flake8)
- 📝 Type errors and suggestions for complex fixes
- 🎯 Files that were modified
- 🧪 Test results (pytest)

## Best practices

1. **Run before commits**: Always lint-fix before committing code
2. **Review changes**: Check auto-fixes don't change logic
3. **Manual fixes**: Address remaining type errors and complex issues manually
4. **Test after**: Run `pytest` to ensure fixes don't break functionality
5. **Type hints**: Add type hints gradually, especially for new code
6. **Flask patterns**: Follow Flask blueprint and service layer patterns

## Related Documentation

- See `README.md` for project overview and setup
- See `tests/README.md` for testing patterns and organization
- See `.cursor/rules/` for project-specific coding patterns and conventions
