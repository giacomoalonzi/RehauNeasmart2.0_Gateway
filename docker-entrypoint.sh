#!/bin/bash
set -e

# Create data directory if it doesn't exist
mkdir -p /data

# Create default options.json if it doesn't exist
if [ ! -f /data/options.json ]; then
    echo "Creating default options.json..."
    cat > /data/options.json <<EOF
{
  "listen_address": "${LISTEN_ADDRESS:-0.0.0.0}",
  "listen_port": "${LISTEN_PORT:-502}",
  "server_type": "${SERVER_TYPE:-tcp}",
  "slave_id": ${SLAVE_ID:-240}
}
EOF
    echo "Default options.json created at /data/options.json"
fi

# Execute the main application
exec "$@"

