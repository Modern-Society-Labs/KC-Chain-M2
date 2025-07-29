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

# Copy application code and startup script
COPY continuous_simulation_service.py .
COPY start.sh .

# Make startup script executable
RUN chmod +x start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Start the application using the startup script
CMD ["./start.sh"]
