FROM python:3.11-slim

WORKDIR /app

# Install system dependencies quickly
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY continuous_simulation_service.py .

# Copy cleansed data files to cleansed_data directory
RUN mkdir -p cleansed_data
COPY *_sensors_*.csv ./cleansed_data/

# Copy wallet mapping into image
COPY wallet_device_mapping.csv .

# Debug: List copied files
RUN ls -la . && ls -la cleansed_data/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Start the application
CMD ["python3", "continuous_simulation_service.py"]
