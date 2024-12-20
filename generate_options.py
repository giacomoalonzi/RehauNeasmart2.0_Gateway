import os
import json

# Get the environment variables
options = {
    "listen_address": os.getenv("LISTEN_ADDRESS", "0.0.0.0"),
    "listen_port": int(os.getenv("LISTEN_PORT", 502)),
    "server_type": os.getenv("SERVER_TYPE", "tcp"),
    "slave_id": int(os.getenv("SLAVE_ID", 240))
}

# Save the options to a file in the /data directory
with open("/data/options.json", "w") as f:
    json.dump(options, f, indent=4)

print("options.json success generated.")