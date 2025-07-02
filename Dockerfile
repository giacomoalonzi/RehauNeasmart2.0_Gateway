# Multi-stage build for optimization
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev make

# Set working directory
WORKDIR /build

# Copy and install requirements
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-alpine

# Install runtime dependencies only
RUN apk add --no-cache libffi curl

# Create non-root user
RUN adduser -D -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser src /app/src

# Create data directory for runtime
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Expose API port
EXPOSE 5000

# Healthcheck for the container
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the refactored application
CMD ["python3", "src/main.py"]