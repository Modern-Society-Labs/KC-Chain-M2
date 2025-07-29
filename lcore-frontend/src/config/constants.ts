// L{CORE} Configuration Constants - Locale Network

// Network Configuration
export const LCORE_CONFIG = {
  LOCALE_NETWORK: {
    chainId: 1205614515668104,
    name: "Locale Network",
    rpcUrl: "https://rpc.devnet.alchemy.com/7eade438-d743-4dc5-ac64-3480de391200",
    contracts: {
      inputBox: "0xC1f612D9ad2270e31BF41fAdBb92f79B63649133",
      cartesiDApp: "0xB7B462b81A10A24e1976C9029Ef8FfBdCFc1a96a",
      deviceRegistry: "0xc3cf289e7d0167a857c28662e673ca7a06d3a461"
    },
    graphqlEndpoint: "https://lcore-iot-node-production.up.railway.app/graphql"
  }
};

// Locale Network Design System Colors
export const LOCALE_COLORS = {
  // Primary Colors
  localeBlue: '#3b82f6',
  smartCityTeal: '#3AB5C4',
  
  // Secondary Colors  
  cloudWhite: '#F5F7FA',
  urbanGrey: '#A3A8B2',
  accentLime: '#C9FF56',
  
  // Tertiary Highlights
  mutedCoral: '#E89B89',
  warmAmber: '#F5B041',
  
  // Data Visualization
  dataGradient: 'linear-gradient(135deg, #3AB5C4 0%, #C9FF56 100%)',
  gridLines: '#E0E0E0'
};

// Device Status Colors
export const DEVICE_STATUS_COLORS = {
  active: '#C9FF56',    // Lime glow for active devices
  idle: '#3AB5C4',      // Teal outline for idle devices  
  error: '#E89B89',     // Muted coral for errors/alerts
  offline: '#A3A8B2'    // Urban grey for offline
};

// Icon mappings for Lucide React
export const LCORE_ICONS = {
  // Core IoT
  sensor: 'Radio',
  dataFlow: 'GitBranch', 
  privacy: 'Lock',
  dashboard: 'BarChart3',
  device: 'Cpu',
  
  // Privacy & Security
  encrypted: 'ShieldCheck',
  zkProof: 'Shield',
  dataWave: 'Waves',
  
  // Status indicators
  active: 'Zap',
  idle: 'Pause',
  error: 'AlertTriangle',
  offline: 'WifiOff',
  
  // Navigation
  home: 'Home',
  devices: 'Smartphone',
  analytics: 'TrendingUp',
  marketplace: 'DollarSign',
  settings: 'Settings',
  
  // Actions
  play: 'Play',
  stop: 'Square',
  refresh: 'RefreshCw',
  download: 'Download',
  upload: 'Upload',
  connect: 'Link',
  disconnect: 'Unlink'
};

// Sensor Type Definitions
export const SENSOR_TYPES = {
  weather: {
    name: 'Weather Station',
    description: 'Temperature, humidity, pressure sensors',
    unit: '°C/%/hPa',
    icon: 'CloudSun',
    color: '#3AB5C4'
  },
  traffic: {
    name: 'Traffic Monitor', 
    description: 'Vehicle count and flow sensors',
    unit: 'vehicles/min',
    icon: 'Car',
    color: '#F5B041'
  },
  energy: {
    name: 'Energy Meter',
    description: 'Power consumption monitoring', 
    unit: 'kWh',
    icon: 'Zap',
    color: '#C9FF56'
  },
  water: {
    name: 'Water Sensor',
    description: 'Flow rate and quality monitoring',
    unit: 'L/min',
    icon: 'Droplets',
    color: '#3AB5C4'
  },
  air_quality: {
    name: 'Air Quality Monitor',
    description: 'PM2.5, CO2, and pollutant levels',
    unit: 'AQI',
    icon: 'Wind',
    color: '#A3A8B2'
  },
  network: {
    name: 'Network Monitor',
    description: 'Connectivity and bandwidth sensors',
    unit: 'Mbps',
    icon: 'Wifi',
    color: '#3b82f6'
  }
};

// Chart Theme Configuration
export const CHART_THEME = {
  colors: {
    primary: '#3AB5C4',
    secondary: '#C9FF56', 
    gradient: 'linear-gradient(135deg, #3AB5C4 0%, #C9FF56 100%)',
    grid: '#E0E0E0',
    text: '#A3A8B2'
  },
  
  elements: {
    point: {
      radius: 6,
      borderWidth: 2,
      backgroundColor: '#C9FF56',
      borderColor: '#3AB5C4'
    },
    
    line: {
      borderWidth: 3,
      tension: 0.4 // Smooth curves
    }
  }
};

// Privacy & Security Constants
export const PRIVACY_CONFIG = {
  encryption: {
    primary: 'AES-256-GCM',
    secondary: 'XChaCha20-Poly1305',
    keyDerivation: 'SHA-256'
  },
  zkProofs: {
    enabled: true,
    provider: 'Cartesi',
    verification: 'on-chain'
  }
};

// Demo & Simulation Constants
export const DEMO_CONFIG = {
  simulationInterval: 5000, // 5 seconds
  maxDataPoints: 50,
  dataRetentionDays: 7,
  realTimeUpdateInterval: 1000 // 1 second
};

// Environment Variables (with fallbacks)
export const ENV = {
  walletConnectProjectId: import.meta.env.VITE_WALLET_CONNECT_PROJECT_ID || '',
  localeNetworkRpc: import.meta.env.VITE_LOCALE_NETWORK_RPC || LCORE_CONFIG.LOCALE_NETWORK.rpcUrl,
  cartesiGraphql: import.meta.env.VITE_CARTESI_GRAPHQL || LCORE_CONFIG.LOCALE_NETWORK.graphqlEndpoint,
  inputBoxAddress: import.meta.env.VITE_INPUT_BOX_ADDRESS || LCORE_CONFIG.LOCALE_NETWORK.contracts.inputBox,
  cartesiDAppAddress: import.meta.env.VITE_CARTESI_DAPP_ADDRESS || LCORE_CONFIG.LOCALE_NETWORK.contracts.cartesiDApp
}; 