# L{CORE} Scripts & Simulation Tools

This directory contains scripts and tools for the L{CORE} IoT system, including data transformation utilities and the continuous simulation service.

## 🚀 **NEW: Continuous Simulation Service**

A real-time IoT device simulation service that provides continuous data generation with live dashboard integration.

### **Features**

✅ **Continuous Operation**: Runs indefinitely until stopped  
✅ **Real-time Control**: Start/stop from frontend dashboard  
✅ **Configurable Interval**: Adjust submission frequency live  
✅ **Resume Functionality**: Maintains state and can resume from where it left off  
✅ **Live Dashboard Updates**: All components update in real-time  
✅ **Real L{CORE} Integration**: Uses actual GraphQL endpoint  
✅ **WebSocket Communication**: Real-time bidirectional communication  
✅ **Device Management**: Tracks and manages multiple simulated devices  
✅ **Comprehensive Metrics**: Live statistics and performance monitoring  

### **Quick Start**

#### **1. Start the Simulation Service**

```bash
# Easy startup (recommended)
./scripts/start_simulation_service.sh

# Or manual startup
python3 scripts/continuous_simulation_service.py

# Development mode with auto-reload
./scripts/start_simulation_service.sh --reload

# Custom host/port
./scripts/start_simulation_service.sh --host 0.0.0.0 --port 9000
```

#### **2. Start the Frontend Dashboard**

```bash
cd lcore-frontend
npm run dev
```

#### **3. Control the Simulation**

- Use the enhanced **Device Simulator** panel in the dashboard
- Adjust the interval in real-time (0.1 to 300 seconds)
- Watch live metrics update across all dashboard components
- Start/stop simulation with resume functionality

### **API Endpoints**

The simulation service provides a REST API and WebSocket interface:

```bash
# Health check
curl http://localhost:8080/health

# Start simulation
curl -X POST http://localhost:8080/simulation/start

# Stop simulation  
curl -X POST http://localhost:8080/simulation/stop

# Update interval
curl -X PUT http://localhost:8080/simulation/interval \
  -H "Content-Type: application/json" \
  -d '{"interval": 3.0}'

# Get status
curl http://localhost:8080/simulation/status

# Get active devices
curl http://localhost:8080/simulation/devices

# WebSocket for real-time updates
ws://localhost:8080/ws
```

### **Frontend Integration**

The continuous simulation service integrates with the following dashboard components:

#### **Enhanced Components**

1. **Device Simulator Panel**
   - Real-time start/stop control
   - Live interval adjustment
   - Device status monitoring
   - Submission statistics

2. **Live Community Metrics**
   - Active device count
   - Data points per hour
   - Privacy compliance score
   - Community earnings estimate

3. **Real-Time Data Flow**
   - Live processing visualization
   - Automatic GraphQL polling
   - Device submission tracking

4. **Recent Activity Feed**
   - Live device submissions
   - Real-time processing updates

#### **WebSocket Integration**

The frontend automatically connects to the simulation service via WebSocket for real-time updates:

```typescript
// Example usage in React components
import { useSimulationService } from '../hooks/useSimulationService';

const MyComponent = () => {
  const { 
    status,           // Simulation status
    devices,          // Active devices
    connected,        // WebSocket connection status
    startSimulation,  // Start function
    stopSimulation,   // Stop function
    updateInterval    // Update interval function
  } = useSimulationService();

  // Component automatically updates when simulation state changes
};
```

### **Data Sources**

The simulation service uses real transformed IoT datasets:

| Domain | Dataset | Records | Source |
|--------|---------|---------|--------|
| **Environmental** | `environmental_sensors_combined.csv` | 2,000 | Air + Water quality fusion |
| **Agricultural** | `agricultural_sensors_transformed.csv` | 30,000 | Plant research → IoT time-series |
| **Health** | `health_sensors_privacy_protected.csv` | 1,000 | Privacy-protected fitness data |
| **Network** | `network_sensors_parsed.csv` | 400 | 5G performance metrics |
| **Retail** | `retail_sensors_anonymized.csv` | 2,823 | PII-anonymized sales data |
| **Weather** | `weather_sensors_converted.csv` | 8,760 | Temperature unit conversion |

**Total**: 44,983 real IoT sensor readings

### **Privacy Protection**

All simulated data maintains privacy protection:

- ✅ **0% PII Retention**: No personal information exposed
- ✅ **Location Anonymization**: Geographic data abstracted
- ✅ **W3C DID Compliance**: Standardized device identity
- ✅ **Encryption Ready**: All data prepared for dual encryption
- ✅ **Community Safe**: Aggregated metrics without individual exposure

### **Performance Metrics**

The simulation service provides comprehensive performance monitoring:

```json
{
  "devices_active": 20,
  "total_submissions": 1247,
  "successful_submissions": 1245,
  "failed_submissions": 2,
  "uptime_seconds": 3600,
  "privacy_validations": 1245,
  "data_points_processed": 1245
}
```

### **Development Mode**

For development and testing:

```bash
# Start with auto-reload
./scripts/start_simulation_service.sh --reload

# The service will automatically restart when code changes
# WebSocket connections will be maintained across restarts
```

### **Troubleshooting**

#### **Common Issues**

1. **Port already in use**
   ```bash
   # Use a different port
   ./scripts/start_simulation_service.sh --port 9000
   ```

2. **WebSocket connection failed**
   - Check if the simulation service is running
   - Verify the port matches in the frontend configuration
   - Check browser console for connection errors

3. **No datasets found**
   - The service will use synthetic data as fallback
   - Run the data transformation scripts to generate real datasets
   - Check the `cleansed_data/` directory

4. **Frontend not updating**
   - Verify WebSocket connection in browser dev tools
   - Check that the simulation service is actually running
   - Restart both services if needed

#### **Logs & Debugging**

The simulation service provides detailed logging:

```
[12:34:56.789] INFO: L{CORE} Continuous Simulator initialized
[12:34:56.791] INFO: Loading transformed IoT datasets...
[12:34:56.920] INFO: Loaded environmental: 2000 records
[12:34:56.955] INFO: Loaded weather: 8760 records
[12:34:57.001] INFO: Total records available: 44983
[12:34:57.002] INFO: L{CORE} Continuous Simulation Service starting up...
[12:34:57.010] INFO: Starting service on localhost:8080
```

---

## **Existing Scripts**

### **Data Transformation Scripts**

Located in `/data_transformation/` directory:

- `environmental_fusion.py` - Combines air + water quality data
- `agriculture_transformation.py` - Converts static research data to IoT time-series
- `health_privacy_protection.py` - Removes location data from fitness trackers
- `network_performance_parsing.py` - Parses network metrics from strings
- `retail_pii_anonymization.py` - Removes customer PII + adds KC neighborhoods
- `weather_unit_conversion.py` - Converts Fahrenheit to Celsius
- `run_all_transformations.py` - Master script to run all transformations

### **Docker Testing**

- `docker_simulator_test.py` - Docker-based testing environment
- `Dockerfile` - Docker image for testing
- `run_simulator_docker.sh` - Docker test execution script

### **Utility Scripts**

- `create_wallet_device_mapping.py` - Device-to-wallet mapping utilities

### **Requirements**

- `requirements_simulator.txt` - Python dependencies for simulation service
- `requirements_wallet_mapping.txt` - Dependencies for wallet mapping utilities

---

## **Getting Started**

### **Prerequisites**

- Python 3.8+
- Node.js 18+ (for frontend)
- All dependencies from requirements files

### **Full System Setup**

1. **Install Python dependencies**
   ```bash
   pip3 install -r scripts/requirements_simulator.txt
   ```

2. **Start the simulation service**
   ```bash
   ./scripts/start_simulation_service.sh
   ```

3. **In another terminal, start the frontend**
   ```bash
   cd lcore-frontend
   npm install
   npm run dev
   ```

4. **Open the dashboard**
   - Visit http://localhost:3000
   - Navigate to the Device Simulator panel
   - Click "Start Simulation" to begin continuous operation

### **Expected Workflow**

1. **Dashboard loads** → WebSocket connects to simulation service
2. **Click "Start Simulation"** → Service begins generating device data
3. **Adjust interval** → Real-time configuration updates
4. **Monitor metrics** → Live updates across all dashboard components
5. **View device activity** → Individual device submission tracking
6. **Stop/resume** → Full state management and resume capability

### **Integration with L{CORE} Infrastructure**

The simulation service integrates with the complete L{CORE} system:

- **GraphQL API**: https://lcore-iot-node-production.up.railway.app/graphql
- **Cartesi Processing**: Simulated fraud-proof data processing
- **Smart Contracts**: InputBox and DeviceRegistry on KC-Chain
- **Privacy Protection**: Dual encryption and DID compliance
- **Community Access**: Privacy-preserving data sharing

This provides a complete end-to-end demonstration of the L{CORE} IoT data pipeline from device simulation through community data access. 