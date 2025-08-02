FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including git for Foundry
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Foundry
RUN curl -L https://foundry.paradigm.xyz | bash
RUN /root/.foundry/bin/foundryup
ENV PATH="/root/.foundry/bin:${PATH}"

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY continuous_simulation_service.py .

# Copy data folder with all CSV files
COPY data/ ./data/

# Debug: List copied files and verify foundry
RUN ls -la . && ls -la data/ && which cast

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Start the application
CMD ["python3", "continuous_simulation_service.py"]