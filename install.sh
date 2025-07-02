#!/bin/bash

# Rehau Neasmart 2.0 Gateway - Installation Helper
# This script helps set up the refactored gateway application

echo "============================================"
echo "Rehau Neasmart 2.0 Gateway - Installation"
echo "============================================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo "Creating data directory..."
    mkdir -p data
    echo "✓ Data directory created"
fi

# Create default config if it doesn't exist
if [ ! -f "data/config.json" ]; then
    echo "Creating default configuration..."
    cat > data/config.json << 'EOF'
{
  "server": {
    "type": "tcp",
    "address": "0.0.0.0",
    "port": 502
  },
  "modbus": {
    "slave_id": 240,
    "sync_on_startup": false,
    "circuit_breaker_failure_threshold": 5,
    "circuit_breaker_recovery_timeout": 60
  },
  "api": {
    "host": "0.0.0.0",
    "port": 5000,
    "enable_auth": false,
    "rate_limit_per_minute": 60,
    "enable_cors": true
  },
  "database": {
    "path": "./data/registers.db",
    "enable_fallback": true,
    "retry_max_attempts": 3
  },
  "logging": {
    "level": "INFO",
    "enable_file": true,
    "file_path": "./data/gateway.log",
    "enable_console": true
  },
  "debug_mode": false
}
EOF
    echo "✓ Default configuration created at data/config.json"
    echo ""
    echo "⚠️  IMPORTANT: Edit data/config.json with your Modbus device settings!"
else
    echo "✓ Configuration file already exists"
fi

echo ""
echo "============================================"
echo "Installation complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Edit data/config.json with your Modbus device settings"
echo "2. Run the application:"
echo "   - Development: python src/main_v2.py"
echo "   - Production: gunicorn --config src/gunicorn_config.py main_v2:app"
echo ""
echo "For more information, see README.md" 