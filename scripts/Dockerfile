FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY scripts/requirements_simulator.txt /app/
RUN pip install --no-cache-dir -r requirements_simulator.txt

# Copy project files
COPY data_transformation/ /app/data_transformation/
COPY scripts/docker_simulator_test.py /app/scripts/
COPY README /app/README

# Create directories for test data and results
RUN mkdir -p /tmp/simulator_test_data
RUN mkdir -p /app/test_results

# Set environment variables
ENV PYTHONPATH="/app"
ENV LCORE_NODE_URL="http://45.55.204.196:8000/graphql"

# Make the test script executable
RUN chmod +x /app/scripts/docker_simulator_test.py

# Create a test runner script
RUN echo '#!/bin/bash\n\
echo "L{CORE} IoT Simulator Test Environment"\n\
echo "===================================="\n\
echo "Starting comprehensive test suite..."\n\
echo ""\n\
python3 /app/scripts/docker_simulator_test.py\n\
echo ""\n\
echo "Test results saved to /app/test_results/"\n\
echo "Logs available in container at /tmp/iot_simulator_test_report.json"\n\
' > /app/run_tests.sh && chmod +x /app/run_tests.sh

# Expose port for potential web interface
EXPOSE 8080

# Default command
CMD ["/app/run_tests.sh"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://45.55.204.196:8000/health || exit 1

# Labels
LABEL maintainer="Modern Society Labs"
LABEL description="L{CORE} IoT Simulator Test Environment"
LABEL version="1.0" 