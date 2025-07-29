#!/bin/bash
set -e

# Get port from Railway or default to 8080
PORT=${PORT:-8080}

echo "Starting L{CORE} simulation service on port $PORT"

# Start the Python application
exec python3 continuous_simulation_service.py --host 0.0.0.0 --port "$PORT"
