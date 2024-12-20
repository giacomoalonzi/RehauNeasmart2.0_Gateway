# Rehau Neasmart 2.0 Gateway

> **Disclaimer**: This is a Docker-based port of the [original project](https://github.com/MatteoManzoni/RehauNeasmart2.0_Gateway), designed for integration with Home Assistant. It acts as a bridge between the Rehau Neasmart 2.0 SysBus (Modbus variant) and Home Assistant, exposing it as a climate entity.

## Overview

This project provides a gateway to integrate **Rehau Neasmart 2.0** with **Home Assistant** via REST APIs. It enables communication over both Modbus TCP and Modbus Serial, allowing for versatile deployment scenarios. The gateway is designed for core Home Assistant installations and supports persistent register storage.

### Key Features

- **REST API** for easy interaction.
- Modbus TCP and Serial (RS485) support.
- SQLite-based persistent register storage.
- Configurable via environment variables.
- Dockerized for portability.

---

## Installation

### Prerequisites

- Docker installed on your system.
- Access to the Rehau Neasmart 2.0 SysBus interface.
- Optional: RS485-to-TCP adapter (e.g., Waveshare RS485 PoE Gateway).

### Setup Steps

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/RehauNeasmart2.0_Gateway.git
   cd RehauNeasmart2.0_Gateway
   ```

2. **Build the Docker Image**:

   ```bash
   docker build -t rehauneasmart-gateway .
   ```

3. **Run the Docker Container**:
   ```bash
   docker run -d \
       --name rehauneasmart-gateway \
       -p 502:502 \
       -e LISTEN_ADDRESS="0.0.0.0" \
       -e LISTEN_PORT=502 \
       -e SERVER_TYPE="tcp" \
       -e SLAVE_ID=240 \
       rehauneasmart-gateway
   ```

---

## REST API Reference

Below are the available API endpoints for interacting with the gateway.

### **1. Check Gateway Health**

- **Endpoint**: `GET /health`
- **Description**: Check if the gateway is running properly.
- **Example**:
  ```bash
  curl -X GET http://localhost:5000/health
  ```
  **Response**:
  ```
  OK
  ```

---

### **2. Read Zone Information**

- **Endpoint**: `GET /zones/<base_id>/<zone_id>`
- **Description**: Retrieve the current state, setpoint, temperature, and humidity of a specific zone.
- **Example**:
  ```bash
  curl -X GET http://localhost:5000/zones/1/1
  ```
  **Response**:
  ```json
  {
    "state": 3,
    "setpoint": 21.5,
    "temperature": 22.0,
    "relative_humidity": 45
  }
  ```

---

### **3. Set Zone Parameters**

- **Endpoint**: `POST /zones/<base_id>/<zone_id>`
- **Description**: Update the operating state or setpoint of a specific zone.
- **Example**:
  ```bash
  curl -X POST http://localhost:5000/zones/1/1 \
  -H "Content-Type: application/json" \
  -d '{"setpoint": 22.5}'
  ```
  **Response**:
  ```json
  {
    "dpt_9001_setpoint": [28729]
  }
  ```

---

### **4. Retrieve Outside Temperature**

- **Endpoint**: `GET /outsidetemperature`
- **Description**: Get the current outside temperature and filtered outside temperature.
- **Example**:
  ```bash
  curl -X GET http://localhost:5000/outsidetemperature
  ```
  **Response**:
  ```json
  {
    "outside_temperature": 15.2,
    "filtered_outside_temperature": 15.0
  }
  ```

---

## Configuration

The container supports the following environment variables for configuration:

| Variable         | Description                          | Default   |
| ---------------- | ------------------------------------ | --------- |
| `LISTEN_ADDRESS` | Address to bind the server.          | `0.0.0.0` |
| `LISTEN_PORT`    | Port to listen for connections.      | `502`     |
| `SERVER_TYPE`    | Connection type (`tcp` or `serial`). | `tcp`     |
| `SLAVE_ID`       | Modbus slave ID.                     | `240`     |

---

## Debugging Tips

- **Check Logs**:
  Use `docker logs` to view container logs for debugging.

  ```bash
  docker logs rehauneasmart-gateway
  ```

- **Inspect SQLite Database**:
  The register state is stored in `/data/registers.db`. Use any SQLite browser to inspect its contents.

- **Rebuild Container**:
  If changes are made to the code, rebuild the container:
  ```bash
  docker build --no-cache -t rehauneasmart-gateway .
  ```

---

## Known Issues

1. **Database Initialization**:

   - On first startup, the database initializes with zeroed registers. You may need to manually update them to start reflecting changes.

2. **Register Updates**:

   - If changes occur via other means (e.g., thermostat or app) while the gateway is down, the values may not sync automatically.

3. **Flask Development Server**:
   - The gateway uses Flask’s development server, which is not optimized for high concurrency.

---

## Contributing

Contributions are welcome! Please follow these steps to submit a pull request:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## Support

For any questions or issues, open an issue on [GitHub](https://github.com/your-username/RehauNeasmart2.0_Gateway/issues).
