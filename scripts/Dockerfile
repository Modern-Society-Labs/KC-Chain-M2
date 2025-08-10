FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Foundry (for 'cast')
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates bash git build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Install Foundry toolchain and ensure 'cast' is on PATH
ENV FOUNDRY_DIR=/root/.foundry
RUN curl -L https://foundry.paradigm.xyz | bash && \
    /root/.foundry/bin/foundryup && \
    ln -s /root/.foundry/bin/cast /usr/local/bin/cast

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY continuous_simulation_service.py .

# Copy data files
COPY data/ ./data/
COPY wallet_device_mapping.csv ./

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Start the application
CMD ["python3", "continuous_simulation_service.py", "--host", "0.0.0.0", "--port", "8080"] 