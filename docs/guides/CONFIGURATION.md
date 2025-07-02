# Configuration Guide

This guide explains how to configure the Rehau Neasmart 2.0 Gateway. The gateway now supports **both modular and traditional configuration methods**:

1. **🆕 Modular Configuration** - Separate files for different domains (Recommended)
2. **📁 Traditional Configuration** - Single config.json file (Still supported)
3. **🔧 Environment Variables** - Runtime/deployment overrides

## Configuration Philosophy

### When to use Modular Configuration:

- **Better organization** - Each domain has its own file
- **Team collaboration** - Different team members can edit different aspects
- **Easier maintenance** - Find and edit specific configurations quickly
- **Selective deployment** - Deploy only certain configuration changes

### When to use Environment Variables:

- **Secrets** (API keys, JWT secrets, passwords)
- **Deployment-specific values** (file paths, IP addresses, ports)
- **Runtime flags** (debug mode, log levels)
- **Docker/production overrides**

---

## Part 1: Modular Configuration (Recommended)

The new modular configuration splits your settings into domain-specific files in the `config/` directory.

### Configuration Structure

```
config/
├── main.json           # Main orchestrator (optional)
├── server.json         # Modbus/server connections
├── api.json           # REST API settings
├── database.json      # Database configuration
├── logging.json       # Logging configuration
├── zones.json         # Building structure
└── features.json      # Feature flags
```

### Getting Started

1. **Copy the example configuration:**

   ```bash
   cp -r config.example config
   ```

2. **Edit the files you need:**

   - `server.json` - Update your Modbus connection details
   - `zones.json` - Define your building structure
   - `api.json` - Adjust API settings if needed

3. **The gateway will auto-detect and load all modules**

### Individual Configuration Files

#### server.json - Hardware Connection

```json
{
  "server": {
    "type": "tcp",
    "address": "192.168.1.100",
    "port": 502
  },
  "modbus": {
    "slave_id": 240,
    "sync_on_startup": false,
    "circuit_breaker_failure_threshold": 5,
    "circuit_breaker_recovery_timeout": 60
  }
}
```

#### api.json - REST API Settings

```json
{
  "api": {
    "host": "0.0.0.0",
    "port": 5001,
    "enable_auth": false,
    "rate_limit_per_minute": 60,
    "enable_cors": true,
    "temperature_unit": "C"
  }
}
```

#### database.json - Data Persistence

```json
{
  "database": {
    "path": "./data/registers.db",
    "enable_fallback": true,
    "retry_max_attempts": 3
  }
}
```

#### logging.json - Application Logs

```json
{
  "logging": {
    "level": "INFO",
    "file_path": "./data/gateway.log",
    "enable_console": true,
    "enable_file": true
  }
}
```

#### zones.json - Building Structure

```json
{
  "structures": [
    {
      "base_id": 1,
      "base_label": "First Floor",
      "zones": [
        { "id": 1, "label": "Living Room" },
        { "id": 2, "label": "Kitchen" }
      ]
    }
  ]
}
```

#### features.json - Feature Flags

```json
{
  "features": {
    "enable_health_endpoint": true,
    "enable_metrics": true,
    "enable_swagger": true,
    "debug_mode": false
  }
}
```

### Advanced: Main Configuration File

You can optionally use `config/main.json` to orchestrate modules and apply overrides:

```json
{
  "config_modules": {
    "server": "./config/server.json",
    "api": "./config/api.json",
    "database": "./config/database.json",
    "logging": "./config/logging.json",
    "zones": "./config/zones.json",
    "features": "./config/features.json"
  },
  "overrides": {
    "server.address": "192.168.1.200",
    "api.port": 8080,
    "debug_mode": true
  }
}
```

---

## Part 2: Traditional Configuration (Legacy)

If you prefer a single configuration file, the gateway still supports the traditional `data/config.json` approach.

### Location

```
data/config.json
```

### Complete Example

```json
{
  "server": {
    "type": "tcp",
    "address": "192.168.1.100",
    "port": 502
  },
  "modbus": {
    "slave_id": 240
  },
  "api": {
    "host": "0.0.0.0",
    "port": 5001,
    "enable_auth": false
  },
  "database": {
    "path": "./data/registers.db",
    "enable_fallback": true
  },
  "logging": {
    "level": "INFO",
    "file_path": "./data/gateway.log"
  },
  "structures": [
    {
      "base_id": 1,
      "base_label": "First Floor",
      "zones": [
        { "id": 1, "label": "Living Room" },
        { "id": 2, "label": "Kitchen" }
      ]
    }
  ],
  "debug_mode": false
}
```

---

## Part 3: Environment Variables

Environment variables override any file configuration and should be used for deployment-specific settings.

### Variable Naming

All variables use the prefix `NEASMART_` followed by the configuration path:

- `NEASMART_API_PORT` → `api.port`
- `NEASMART_MODBUS_SLAVE_ID` → `modbus.slave_id`
- `NEASMART_DEBUG_MODE` → `debug_mode`

### Secrets (Environment Variables Only)

These should **NEVER** be in configuration files:

```bash
# Authentication (use only if api.enable_auth = true in config)
NEASMART_API_KEY=your-secret-api-key-here
NEASMART_API_JWT_SECRET=your-jwt-secret-here
```

### Deployment Overrides

```bash
# Production overrides
NEASMART_DEBUG_MODE=false
NEASMART_LOG_LEVEL=WARNING
NEASMART_API_HOST=0.0.0.0
NEASMART_API_PORT=5000

# Development overrides
NEASMART_DEBUG_MODE=true
NEASMART_LOG_LEVEL=DEBUG
NEASMART_GATEWAY_SERVER_ADDRESS=localhost
```

---

## Configuration Priority

The gateway loads configuration in this order (later overrides earlier):

1. **Default values** (hardcoded defaults)
2. **Configuration files** (modular or traditional)
3. **Environment variables** (highest priority)

### Auto-Detection Logic

The gateway automatically detects your configuration setup:

1. **Look for `config/main.json`** - Use modular with orchestrator
2. **Look for `config/` directory** - Use modular auto-detection
3. **Look for `data/config.json`** - Use traditional single file
4. **Use defaults** - If nothing found

---

## Migration Guide

### From Traditional to Modular

1. **Create config directory:**

   ```bash
   mkdir config
   ```

2. **Split your existing config.json:**

   ```bash
   # Use the provided example as a template
   cp -r config.example config
   # Then copy your specific values from data/config.json
   ```

3. **Test the new configuration:**

   ```bash
   python src/main.py
   # Check logs for "Using modular configuration"
   ```

4. **Optional: Remove old config:**
   ```bash
   # Once you're confident the new config works
   mv data/config.json data/config.json.backup
   ```

---

## Best Practices

### Organization

1. **Use modular configuration** for new deployments
2. **Keep zones.json separate** - this changes most frequently
3. **Use main.json sparingly** - only for complex override scenarios
4. **Document your specific setup** for your team

### Security

1. **Never commit secrets** to configuration files
2. **Use environment variables** for all sensitive data
3. **Set appropriate file permissions** (600) on config files
4. **Use different API keys** for different environments

### Deployment

1. **Use config.example as a template** for new environments
2. **Version control your config files** (except secrets)
3. **Test configuration changes** in development first
4. **Use environment variables** for environment-specific values

---

## Troubleshooting

### Common Issues

1. **"No configuration found"**

   - Check if `config/` directory exists with valid JSON files
   - Verify `NEASMART_CONFIG_FILE` environment variable
   - Look for `data/config.json` as fallback

2. **"Invalid JSON in configuration file"**

   - Validate JSON syntax in individual module files
   - Check for trailing commas in JSON

3. **"No structures defined"**

   - Ensure `zones.json` exists with `structures` array
   - Check `structures` field name (not `zones`)

4. **Environment variables not working**

   - Verify variable names have `NEASMART_` prefix
   - Check variable is exported in shell
   - Restart application after setting variables

5. **Modular config not loading**
   - Ensure files are in `config/` directory (not `config.example/`)
   - Check file permissions (must be readable)
   - Look for syntax errors in individual JSON files

### Debugging Configuration

```bash
# Check which configuration is being used
python -c "
from src.config import load_config
config = load_config()
print(f'Database: {config.database.path}')
print(f'Zones: {len(config.structures)} structures loaded')
"

# Validate specific config file
python -c "
import json
with open('config/zones.json') as f:
    config = json.load(f)
    print('zones.json is valid JSON')
    print(f'Structures: {len(config.get("structures", []))}')
"
```

For more help, see [Troubleshooting Guide](../README.md#troubleshooting).
