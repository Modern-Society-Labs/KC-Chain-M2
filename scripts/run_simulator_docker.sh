#!/bin/bash

# L{CORE} IoT Simulator Docker Runner
# ==================================

echo "Building L{CORE} IoT Simulator Docker Container..."
echo ""

# Build the Docker image
docker build -f scripts/Dockerfile -t lcore-iot-simulator:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker image built successfully!"
echo ""
echo "Running L{CORE} IoT Simulator Test Suite..."
echo "==========================================="

# Run the container with volume mount for results
docker run --rm \
    -v "$(pwd)/test_results:/app/test_results" \
    -e LCORE_NODE_URL="${LCORE_NODE_URL:-http://45.55.204.196:8000/graphql}" \
    --name lcore-iot-simulator \
    lcore-iot-simulator:latest

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Test suite completed successfully!"
    echo "📊 Test results saved to: ./test_results/"
    echo ""
    echo "To view detailed test report:"
    echo "  cat ./test_results/iot_simulator_test_report.json"
else
    echo ""
    echo "❌ Test suite failed!"
    echo "Check the logs above for error details"
    exit 1
fi 