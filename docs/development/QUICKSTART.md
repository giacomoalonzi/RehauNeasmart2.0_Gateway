# Quick Start Commands

This guide provides common commands for development and operations without using Make.

## Development Commands

### Setup Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run Application

```bash
# Development mode
cd src && python main.py

# With debug logging
NEASMART_LOG_LEVEL=DEBUG python src/main.py

# Production mode (if Gunicorn is available)
cd src && gunicorn --config gunicorn_config.py main:app
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/ -v
pytest tests/unit/test_database.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Check formatting
black src/ tests/ --check

# Lint code
flake8 src/ tests/ --max-line-length=100

# Type checking
mypy src/ --ignore-missing-imports
```

### Docker Operations

```bash
# Build image
docker build -t rehau-neasmart-gateway:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Access container shell
docker exec -it rehau-neasmart-gateway /bin/sh
```

### Database Operations

```bash
# Backup database
cp data/registers.db data/registers_backup_$(date +%Y%m%d_%H%M%S).db

# Reset database
rm -f data/registers.db
```

### Configuration

```bash
# Create config from example
cp data/config.json.example data/config.json

# Validate JSON syntax
python -m json.tool data/config.json > /dev/null && echo "Configuration is valid"

# Create .env file
cp env.example .env
```

### Cleaning

```bash
# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Remove test artifacts
rm -rf .pytest_cache/
rm -rf htmlcov/
rm -f .coverage
```

## Common Workflows

### Fresh Development Setup

```bash
# 1. Clone and setup
git clone <repository-url>
cd RehauNeasmart2.0_Gateway

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp data/config.json.example data/config.json
# Edit data/config.json with your settings

# 5. Run
cd src && python main.py
```

### Before Committing

```bash
# 1. Format code
black src/ tests/

# 2. Run linter
flake8 src/ tests/

# 3. Run tests
pytest tests/ -v

# 4. Check everything passes
black src/ tests/ --check && flake8 src/ tests/ && pytest tests/
```

### Docker Deployment

```bash
# 1. Configure environment
cp env.example .env
# Edit .env with your settings

# 2. Build and run
docker-compose up -d

# 3. Check status
docker-compose ps
docker-compose logs --tail=50
```

## Tips

- Use shell aliases for common commands
- Consider using `direnv` for automatic environment activation
- Use VS Code tasks.json for IDE integration
- Create shell scripts for complex workflows

## Shell Aliases Example

Add to your `.bashrc` or `.zshrc`:

```bash
# Rehau Neasmart aliases
alias rn-run='cd ~/RehauNeasmart2.0_Gateway && source venv/bin/activate && cd src && python main.py'
alias rn-test='cd ~/RehauNeasmart2.0_Gateway && source venv/bin/activate && pytest tests/ -v'
alias rn-format='cd ~/RehauNeasmart2.0_Gateway && source venv/bin/activate && black src/ tests/'
alias rn-lint='cd ~/RehauNeasmart2.0_Gateway && source venv/bin/activate && flake8 src/ tests/'
```
