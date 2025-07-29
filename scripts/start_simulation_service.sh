#!/bin/bash
# L{CORE} Continuous Simulation Service Startup Script
# ===================================================

set -e

echo "🚀 Starting L{CORE} Continuous Simulation Service..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "scripts/continuous_simulation_service.py" ]; then
    print_error "continuous_simulation_service.py not found. Please run this script from the KC-Chain-M2 root directory."
    exit 1
fi

# Check if datasets exist
print_status "Checking for transformed datasets..."
if [ ! -d "cleansed_data" ]; then
    print_warning "cleansed_data directory not found. The simulation will use synthetic data."
else
    dataset_count=$(ls cleansed_data/*.csv 2>/dev/null | wc -l)
    if [ $dataset_count -gt 0 ]; then
        print_success "Found $dataset_count transformed datasets"
    else
        print_warning "No CSV files found in cleansed_data. Using synthetic data."
    fi
fi

# Check Python version
print_status "Checking Python version..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python $python_version found"
else
    print_error "Python 3 is required but not found"
    exit 1
fi

# Install/check dependencies
print_status "Checking dependencies..."
if pip3 install -r scripts/requirements_simulator.txt > /dev/null 2>&1; then
    print_success "Dependencies satisfied"
else
    print_error "Failed to install dependencies. Please check scripts/requirements_simulator.txt"
    exit 1
fi

# Parse command line arguments
HOST="localhost"
PORT="8080"
RELOAD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --reload)
            RELOAD=true
            shift
            ;;
        --help|-h)
            echo "L{CORE} Continuous Simulation Service Startup Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --host HOST     Host to bind to (default: localhost)"
            echo "  --port PORT     Port to bind to (default: 8080)"
            echo "  --reload        Enable auto-reload for development"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Start on localhost:8080"
            echo "  $0 --host 0.0.0.0          # Start on all interfaces"
            echo "  $0 --port 9000 --reload    # Development mode on port 9000"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if port is available
print_status "Checking if port $PORT is available..."
if netstat -an 2>/dev/null | grep ":$PORT " > /dev/null; then
    print_warning "Port $PORT appears to be in use. The service may fail to start."
else
    print_success "Port $PORT is available"
fi

# Display startup information
echo ""
echo "📊 L{CORE} Continuous Simulation Service"
echo "========================================"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Reload: $RELOAD"
echo "GraphQL Endpoint: https://lcore-iot-node-production.up.railway.app/graphql"
echo ""
echo "API Endpoints will be available at:"
echo "  • Health Check: http://$HOST:$PORT/health"
echo "  • Start Simulation: http://$HOST:$PORT/simulation/start"
echo "  • Stop Simulation: http://$HOST:$PORT/simulation/stop"
echo "  • WebSocket: ws://$HOST:$PORT/ws"
echo ""
echo "Frontend Integration:"
echo "  Make sure your React frontend is configured to connect to:"
echo "  • REST API: http://$HOST:$PORT"
echo "  • WebSocket: ws://$HOST:$PORT/ws"
echo ""

# Build command
CMD="python3 scripts/continuous_simulation_service.py --host $HOST --port $PORT"
if [ "$RELOAD" = true ]; then
    CMD="$CMD --reload"
fi

print_status "Starting simulation service..."
echo "Command: $CMD"
echo ""

# Start the service
exec $CMD 