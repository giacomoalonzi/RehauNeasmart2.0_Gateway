# Use a lightweight Python base image
FROM python:3.9-alpine

# Install system dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev make

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker's layer caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src /app/src

# Copy the data directory (including options.json)
COPY data /app/data


# Healthcheck for the container
HEALTHCHECK --interval=2m --timeout=3s \
    CMD curl -f http://localhost:5000/health || exit 1

# Define the entrypoint
CMD ["python3", "src/main.py"]