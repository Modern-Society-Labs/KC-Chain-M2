# 🧪 L{CORE} IoT Dashboard Testing Guide

## **Quick Demo Verification**

### **1. Prerequisites Check**
```bash
# Check Node.js version (18+ required)
node --version

# Check Python version (3.8+ required)
python3 --version

# Check npm is available
npm --version

# Verify git is installed
git --version
```

### **2. Start Demo Services**

**Terminal 1: Start Simulation Service**
```bash
# Install dependencies first time
pip3 install -r scripts/requirements_simulator.txt

# Start the simulation service
./scripts/start_simulation_service.sh

# Alternative: Start manually
python3 scripts/continuous_simulation_service.py --port 8080
```

**Terminal 2: Start Frontend Dashboard**
```bash
cd lcore-frontend

# Install dependencies first time
npm install

# Start development server
npm run dev
```

### **3. Visual Connection Verification**

Open **http://localhost:3000** and look for these **immediate indicators**:

#### **✅ Connection Success Indicators**

1. **Header Status Indicators**:
   - 🟢 **Green dots** next to "LCore Node", "GraphQL", "Locale Network", "Cartesi Machine"
   - All show **"Online"** status
   - **"Network Active"** with pulsing green dot

2. **Device Simulator Panel**:
   - 🟢 **Green connection dot** visible
   - Status shows **"Stopped"** (not "Service Offline")
   - Start/Stop button is **enabled** (not grayed out)
   - Interval input shows a value (e.g., "10.0")

3. **Community Metrics Panel**:
   - Shows **"Live Community Metrics"** with activity indicator
   - Displays real numbers instead of placeholder values
   - **"Live"** status indicator visible

4. **Recent Activity Panel**:
   - Shows **"Live from Locale Network"** indicator
   - Displays recent blockchain transactions
   - **"20 items"** or similar count visible
   - Refresh indicator and manual refresh button

#### **❌ Connection Failure Indicators**

1. **Device Simulator Panel**:
   - 🔴 **Gray/Red connection indicator**
   - Status shows **"Service Offline"**
   - Start/Stop button **disabled/grayed out**
   - No device count or metrics

2. **Recent Activity Panel**:
   - Shows static placeholder data
   - No real transaction data
   - Missing live indicators

### **4. Browser Developer Tools Check**

**Open DevTools (F12) → Console Tab**

#### **✅ Expected Success Messages**
```
🔗 Connecting to WebSocket: ws://localhost:8080/ws
✅ Connected to simulation service
📊 Initial state received
🔍 Fetching REAL blockchain data via RPC...
📊 Current block number: 84XXX
📦 Retrieved 15 recent blocks
📱 Loaded X IoT device mappings for real-time device identification
```

#### **❌ Error Messages to Watch For**
```
WebSocket connection failed
Error connecting to simulation service
Error fetching REAL blockchain activity via RPC
Failed to load activity
Connection refused
```

#### **✅ Network Tab Verification**
1. **Filter by WS** (WebSocket)
2. Should see: `ws://localhost:8080/ws` with status **101 (Switching Protocols)**
3. **Messages tab** shows real-time data flow

## **Functional Testing Steps**

### **Test 1: Simulation Service Connection**
```bash
# Test API health endpoint
curl http://localhost:8080/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-XX-XX...",
#   "simulation_running": false,
#   "devices_active": 0,
#   "websocket_connections": 1
# }
```

### **Test 2: Start IoT Simulation**
1. Click **"Start Simulation"** in the Device Simulator panel
2. **Watch for immediate changes**:
   - Button changes to **"Stop Simulation"** (red)
   - Status changes to **"Running"**
   - **Device count** starts increasing
   - **Community metrics** begin updating
   - **Console messages** show device submissions

### **Test 3: Blockchain Data Integration**
1. **Recent Activity panel** should show:
   - Real blockchain transactions with timestamps
   - Transaction hashes (clickable links)
   - Device-specific transaction details
   - Mix of regular transactions and IoT submissions

2. **Community Metrics** should display:
   - Live device counts
   - Total submissions
   - Network statistics

### **Test 4: Device Registry**
1. Navigate to **"Devices"** page
2. Should display:
   - **67 IoT devices** in grid layout
   - **Search and filter** functionality
   - **Live status indicators** (Online/Offline)
   - **Device categories** (Health, Retail, Network, etc.)
   - **Clickable wallet addresses** linking to block explorer

### **Test 5: Real-Time Updates**
1. With simulation running, observe:
   - **Numbers incrementing** in Community Metrics
   - **New transactions** appearing in Recent Activity
   - **Device status updates** in Device Registry
   - **WebSocket messages** in browser console

## **Device Registry Testing**

### **Search & Filter Tests**
1. **Search by device name**: Type "health" → should filter to health devices
2. **Filter by category**: Select "Retail" → should show only retail devices  
3. **Online only toggle**: Should filter to only active devices
4. **Clear filters**: Results should reset to all devices

### **Device Card Tests**
1. **Status indicators**: Green dots for online, gray for offline
2. **Wallet links**: Click wallet address → should open block explorer
3. **InputBox counts**: Should show realistic transaction counts
4. **Device details**: Should display category, ID, and last activity

## **Browser Console Testing**

### **Real-Time Data Flow Monitoring**
```javascript
// Monitor WebSocket messages
let wsMessageCount = 0;
const originalWebSocket = window.WebSocket;
window.WebSocket = function(...args) {
  const ws = new originalWebSocket(...args);
  ws.addEventListener('message', (e) => {
    wsMessageCount++;
    console.log(`📡 WS Message #${wsMessageCount}:`, JSON.parse(e.data));
  });
  return ws;
};
```

### **API Testing from Console**
```javascript
// Test simulation service API
fetch('http://localhost:8080/health')
  .then(r => r.json())
  .then(console.log);

// Check simulation status
fetch('http://localhost:8080/simulation/status')
  .then(r => r.json())
  .then(console.log);

// Test blockchain RPC connection
fetch('https://rpc.devnet.alchemy.com/7eade438-d743-4dc5-ac64-3480de391200', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    jsonrpc: '2.0',
    method: 'eth_blockNumber',
    params: [],
    id: 1
  })
})
.then(r => r.json())
.then(data => console.log('Current block:', parseInt(data.result, 16)));
```

## **Common Issues & Solutions**

### **❌ "Service Offline" Never Changes**
**Cause**: Simulation service not running or port conflict

**Solutions**:
```bash
# Check if service is running
lsof -i :8080

# Kill existing process if needed
killall python3

# Restart simulation service
./scripts/start_simulation_service.sh

# Try different port
python3 scripts/continuous_simulation_service.py --port 9000
```

### **❌ Frontend Won't Start**
**Cause**: Node modules or dependencies issue

**Solutions**:
```bash
cd lcore-frontend

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
lsof -i :3000

# Try different port
npm run dev -- --port 3001
```

### **❌ No Blockchain Data**
**Cause**: RPC connection issues or network problems

**Solutions**:
```bash
# Test RPC connection directly
curl -X POST https://rpc.devnet.alchemy.com/7eade438-d743-4dc5-ac64-3480de391200 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# Check internet connection
ping google.com

# Verify environment variables
echo $VITE_RPC_URL
```

### **❌ Devices Show Static Data**
**Cause**: Device mapping not loading or simulation service issues

**Solutions**:
1. Check browser console for mapping load messages
2. Verify `wallet_device_mapping.csv` exists
3. Restart simulation service
4. Clear browser cache (Ctrl+Shift+R)

## **Performance Testing**

### **Load Testing Simulation Service**
```bash
# Test multiple concurrent connections
for i in {1..10}; do
  curl http://localhost:8080/health &
done

# Test WebSocket connections
node -e "
const WebSocket = require('ws');
for(let i = 0; i < 5; i++) {
  const ws = new WebSocket('ws://localhost:8080/ws');
  ws.on('open', () => console.log('Connected', i));
}
"
```

### **Frontend Performance Check**
1. **Open Chrome DevTools** → **Performance tab**
2. **Start recording** → Interact with dashboard → **Stop recording**
3. **Check for**:
   - Frame rate drops
   - Memory leaks
   - Excessive re-renders
   - Network request bottlenecks

## **Demo Testing Checklist**

### **✅ Basic Setup**
- [ ] Node.js 18+ installed
- [ ] Python 3.8+ installed  
- [ ] Dependencies installed (frontend & backend)
- [ ] Both services start without errors

### **✅ Connection Verification**
- [ ] Simulation service health endpoint responds
- [ ] Frontend loads at http://localhost:3000
- [ ] WebSocket connection established
- [ ] Green status indicators visible

### **✅ Real-Time Features**
- [ ] Start simulation button works
- [ ] Device counts increase when simulation runs
- [ ] Recent Activity updates with real transactions
- [ ] Community Metrics show live data
- [ ] Stop simulation button works

### **✅ Device Registry**
- [ ] 67 devices displayed in grid
- [ ] Search functionality works
- [ ] Category filtering works
- [ ] Online/Offline status indicators
- [ ] Wallet addresses are clickable links

### **✅ Blockchain Integration**
- [ ] Recent Activity shows real blockchain data
- [ ] Transaction hashes are valid
- [ ] Block explorer links work
- [ ] RPC calls fetch current block data
- [ ] Device transactions appear in timeline

### **✅ UI/UX**
- [ ] Responsive design works on mobile
- [ ] Logo and branding display correctly
- [ ] Social media links work
- [ ] Help page content is accurate
- [ ] Navigation between pages works

## **Production Deployment Testing**

### **Railway Deployment Verification**
```bash
# Build frontend for production
cd lcore-frontend
npm run build

# Test production build locally
npm run preview

# Deploy simulation service
cd ../scripts
railway up

# Deploy frontend
cd ../lcore-frontend
railway up
```

### **Environment Variables Testing**
1. **Create `.env` files** based on `.env.example`
2. **Test with different RPC URLs**
3. **Verify production vs development settings**
4. **Check CORS settings** for deployed services

## **Success Criteria**

**🎯 Demo is working correctly when:**

1. **✅ Connection**: All status indicators are green
2. **✅ Simulation**: Start/stop controls work and affect real data
3. **✅ Blockchain**: Recent Activity shows live blockchain transactions  
4. **✅ Device Registry**: All 67 devices display with correct status
5. **✅ Real-time**: Data updates automatically every 30 seconds
6. **✅ WebSocket**: Live connection with message flow in DevTools
7. **✅ Links**: All wallet addresses and external links work
8. **✅ Responsive**: Works on desktop, tablet, and mobile
9. **✅ Performance**: No lag or memory leaks during extended use

**If all criteria pass, your L{CORE} IoT Dashboard demo is production-ready!** ✅ 