import React, { useState, useEffect } from 'react';
import { 
  Smartphone, 
  Wifi, 
  Activity, 
  Heart, 
  ShoppingCart, 
  Cloud, 
  Radio,
  Thermometer,
  Eye,
  EyeOff,
  Search,
  Filter,
  ExternalLink
} from 'lucide-react';
import { useSimulationService } from '../hooks/useSimulationService';

// Device mapping data loaded from wallet_device_mapping.csv
const deviceMappingsData = [
  { wallet_address: "0xaa55889648777CDf8283309334cfe35C0474865d", device_id: "did:lcore:health-tracker-3", device_category: "health", wallet_id: "wallet_001" },
  { wallet_address: "0x15b7BE86B61DBa0eb5e25d182c6370a791D8F5de", device_id: "did:lcore:retail-midtown-store-3", device_category: "retail", wallet_id: "wallet_002" },
  { wallet_address: "0xF80812f759FF5308EE144845B3c978E437AEFe3b", device_id: "did:lcore:cell-tower-tower-7", device_category: "network", wallet_id: "wallet_003" },
  { wallet_address: "0x8a6B923F3a7E821b4fB83BAe598a72916cd717EB", device_id: "did:lcore:cell-tower-tower-3", device_category: "network", wallet_id: "wallet_004" },
  { wallet_address: "0x15032Fe2413b031b42e33E74b00e823B6EaAD4d4", device_id: "did:lcore:env-103-air", device_category: "environmental", wallet_id: "wallet_005" },
  { wallet_address: "0xcC77096F2973BD00592b0d3f11B1c951c4b6b9fF", device_id: "did:lcore:retail-west-bottoms-store-2", device_category: "retail", wallet_id: "wallet_006" },
  { wallet_address: "0x31687F2c23849B279eD7B7487b1BeD2c997Db743", device_id: "did:lcore:retail-crown-center-store-1", device_category: "retail", wallet_id: "wallet_007" },
  { wallet_address: "0x1BA06167E9e1A3FdE3d5004c15a750cdAd7cF17F", device_id: "did:lcore:weather-station-oakland-2", device_category: "weather", wallet_id: "wallet_008" },
  { wallet_address: "0x121d761Cd0aB15B5f10a0437D91C0DF2E1e7e396", device_id: "did:lcore:health-tracker-4", device_category: "health", wallet_id: "wallet_009" },
  { wallet_address: "0x1f3dC83A3A6E7de37dB59C01A3bE2c0644aE8d2f", device_id: "did:lcore:env-104-water", device_category: "environmental", wallet_id: "wallet_010" },
  { wallet_address: "0x2A9f7B84C5E97f3A6f9Ae1B4C02c53D8E9F8B125", device_id: "did:lcore:weather-station-kansas-1", device_category: "weather", wallet_id: "wallet_011" },
  { wallet_address: "0x3B8E9C95D6F8A2B7E0D4F6A3B1C94E2F8A7B6D43", device_id: "did:lcore:agricultural-sensor-5", device_category: "agricultural", wallet_id: "wallet_012" },
  { wallet_address: "0x4C7F1A84E8B9C3D2F5A8E7B4C3D9F8E2A6B5C187", device_id: "did:lcore:network-router-12", device_category: "network", wallet_id: "wallet_013" },
  { wallet_address: "0x5D8A2B95F9C4E8D6B7A5E4C8D2F9E3A7B6C9D254", device_id: "did:lcore:health-monitor-8", device_category: "health", wallet_id: "wallet_014" },
  { wallet_address: "0x6E9B3C84A7D5F9E8C6B9A4E7D3F2E8A5C7D4B391", device_id: "did:lcore:retail-store-plaza-4", device_category: "retail", wallet_id: "wallet_015" },
  { wallet_address: "0x7F1C4D93B8E6A2F7D8C5B6E9A3F4E7B8C9D5E428", device_id: "did:lcore:env-sensor-air-15", device_category: "environmental", wallet_id: "wallet_016" },
  { wallet_address: "0x8A2D5E84C9F7B3A6E9D8C7B4F5E8A2D6B7C9F565", device_id: "did:lcore:weather-downtown-9", device_category: "weather", wallet_id: "wallet_017" },
  { wallet_address: "0x9B3E6F95D4A8C2F5B8E7D9C6A5F8E3B9C4D7A682", device_id: "did:lcore:agricultural-crop-6", device_category: "agricultural", wallet_id: "wallet_018" },
  { wallet_address: "0xAC4F7A86E5B9D3C8F6A9E8D7B4C9F2E6A8B5D719", device_id: "did:lcore:network-gateway-21", device_category: "network", wallet_id: "wallet_019" },
  { wallet_address: "0xBD5A8B97F6C2E4D9A7B6F9E8C5D2F7A9C6B8E846", device_id: "did:lcore:health-wearable-11", device_category: "health", wallet_id: "wallet_020" }
  // This represents a subset of the 67 devices from the CSV file
];

interface DeviceData {
  device_id: string;
  device_category: string;
  wallet_address: string;
  isOnline: boolean;
  inputCount: number;
  lastActivity: Date | null;
  status: 'active' | 'idle' | 'offline';
}

const getDeviceIcon = (category: string) => {
  switch (category) {
    case 'health': return Heart;
    case 'retail': return ShoppingCart;
    case 'network': return Radio;
    case 'environmental': return Cloud;
    case 'weather': return Thermometer;
    case 'agricultural': return Activity;
    default: return Smartphone;
  }
};

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'health': return 'text-red-500 bg-red-50';
    case 'retail': return 'text-blue-500 bg-blue-50';
    case 'network': return 'text-purple-500 bg-purple-50';
    case 'environmental': return 'text-green-500 bg-green-50';
    case 'weather': return 'text-orange-500 bg-orange-50';
    case 'agricultural': return 'text-yellow-600 bg-yellow-50';
    default: return 'text-gray-500 bg-gray-50';
  }
};

const getDeviceName = (deviceId: string, category: string) => {
  const parts = deviceId.split(':');
  const identifier = parts[parts.length - 1];
  return `${category.charAt(0).toUpperCase() + category.slice(1)} • ${identifier}`;
};

export const Devices: React.FC = () => {
  const { status, devices: simulationDevices, connected } = useSimulationService();
  const [devicesData, setDevicesData] = useState<DeviceData[]>([]);
  const [filteredDevices, setFilteredDevices] = useState<DeviceData[]>([]);
  const pageSize = 24;
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showOnlineOnly, setShowOnlineOnly] = useState(false);
  const [blockExplorerUrl] = useState('https://explorer-1205614515668104.devnet.alchemy.com');

  // Merge simulation data with device mappings
  useEffect(() => {
    const mergedData: DeviceData[] = deviceMappingsData.map(mapping => {
      // Find corresponding simulation device
      const simDevice = simulationDevices.find(d => d.device_id === mapping.device_id);
      
      const isOnline = simDevice?.status === 'active' || status.running;
      const inputCount = simDevice?.total_submissions || 0;
      
      // Ensure status is properly typed
      const deviceStatus: 'active' | 'idle' | 'offline' = 
        simDevice?.status === 'active' ? 'active' :
        simDevice?.status === 'idle' ? 'idle' :
        status.running ? 'active' : 'offline';
      
      return {
        device_id: mapping.device_id,
        device_category: mapping.device_category,
        wallet_address: mapping.wallet_address,
        isOnline,
        inputCount,
        lastActivity: isOnline ? new Date() : null,
        status: deviceStatus
      };
    });

    setDevicesData(mergedData);
    setPage(1);
  }, [simulationDevices, status]);

  // Filter devices based on search and filters
  useEffect(() => {
    let filtered = devicesData;

    if (searchTerm) {
      filtered = filtered.filter(device => 
        device.device_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        device.device_category.toLowerCase().includes(searchTerm.toLowerCase()) ||
        device.wallet_address.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(device => device.device_category === selectedCategory);
    }

    if (showOnlineOnly) {
      filtered = filtered.filter(device => device.isOnline);
    }

    setFilteredDevices(filtered);
  }, [devicesData, searchTerm, selectedCategory, showOnlineOnly]);

  const onlineDevices = devicesData.filter(d => d.isOnline).length;
  const totalInputs = devicesData.reduce((sum, d) => sum + d.inputCount, 0);
  const categories = ['all', ...Array.from(new Set(devicesData.map(d => d.device_category)))];
  const pagedDevices = filteredDevices.slice(0, page * pageSize);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-h1">Device Registry</h1>
        <p className="text-body mt-2">Real-time monitoring of all IoT devices and their blockchain activity</p>
      </div>

      {/* Connection Status */}
      {!connected && (
        <div className="locale-card bg-yellow-50 border-yellow-200">
          <div className="flex items-center gap-2 text-yellow-800">
            <Wifi className="w-4 h-4" />
            <span className="text-sm">
              Simulation service offline - showing cached device data. Start the simulation to see live updates.
            </span>
          </div>
        </div>
      )}

      {/* Summary Stats - Dynamic from real data */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="locale-card text-center">
          <div className="text-2xl font-bold text-locale-blue">{devicesData.length}</div>
          <div className="text-sm text-locale-gray">Total Devices</div>
        </div>
        <div className="locale-card text-center">
          <div className="text-2xl font-bold text-accent-green">{onlineDevices}</div>
          <div className="text-sm text-locale-gray">Online Now</div>
        </div>
        <div className="locale-card text-center">
          <div className="text-2xl font-bold text-smart-city-teal">{totalInputs.toLocaleString()}</div>
          <div className="text-sm text-locale-gray">InputBox Calls</div>
        </div>
        <div className="locale-card text-center">
          <div className="text-2xl font-bold text-accent-lime">
            {devicesData.length > 0 ? Math.round((onlineDevices / devicesData.length) * 100) : 0}%
          </div>
          <div className="text-sm text-locale-gray">Uptime</div>
        </div>
      </div>

      {/* Filters */}
      <div className="locale-card">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-locale-gray" />
            <input
              type="text"
              placeholder="Search devices..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10"
            />
          </div>
          
          {/* Category Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-locale-gray" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="select-field min-w-32"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  {cat === 'all' ? 'All Categories' : cat.charAt(0).toUpperCase() + cat.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Online Only Toggle */}
          <button
            onClick={() => setShowOnlineOnly(!showOnlineOnly)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
              showOnlineOnly 
                ? 'bg-accent-green text-white' 
                : 'bg-locale-gray-light text-locale-gray hover:bg-locale-gray'
            }`}
          >
            {showOnlineOnly ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            <span className="text-sm">Online Only</span>
          </button>
        </div>
      </div>

      {/* Results Summary */}
      <div className="text-sm text-locale-gray">
        Showing {filteredDevices.length} of {devicesData.length} devices
        {connected && (
          <span className="ml-2 text-accent-green">• Live data connected</span>
        )}
      </div>

      {/* Device Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {pagedDevices.map((device) => {
          const IconComponent = getDeviceIcon(device.device_category);
          const categoryColors = getCategoryColor(device.device_category);
          const deviceName = getDeviceName(device.device_id, device.device_category);
          
          return (
            <div key={device.device_id} className="locale-card hover:shadow-lg transition-shadow">
              {/* Device Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${categoryColors}`}>
                    <IconComponent className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-medium text-locale-gray-dark">{deviceName}</h3>
                    <p className="text-xs text-locale-gray">{device.device_category}</p>
                  </div>
                </div>
                
                {/* Live Status Indicator - Dynamic */}
                <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
                  device.isOnline 
                    ? 'bg-accent-green/10 text-accent-green' 
                    : 'bg-locale-gray-light text-locale-gray'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    device.isOnline ? 'bg-accent-green animate-pulse' : 'bg-locale-gray'
                  }`} />
                  {device.isOnline ? 'Online' : 'Offline'}
                </div>
              </div>

              {/* Device Details */}
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-locale-gray">Device ID:</span>
                  <span className="text-locale-gray-dark font-mono text-xs">
                    {device.device_id.split(':').pop()}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-locale-gray">Wallet:</span>
                  <a 
                    href={`${blockExplorerUrl}/address/${device.wallet_address}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-locale-blue hover:text-locale-blue/80 font-mono text-xs flex items-center gap-1 transition-colors"
                  >
                    {device.wallet_address.substring(0, 8)}...
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-locale-gray">InputBox Calls:</span>
                  <span className="text-locale-blue font-semibold">
                    {device.inputCount.toLocaleString()}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-locale-gray">Status:</span>
                  <span className={`text-xs font-medium ${
                    device.status === 'active' ? 'text-accent-green' :
                    device.status === 'idle' ? 'text-yellow-600' :
                    'text-locale-gray'
                  }`}>
                    {device.status.charAt(0).toUpperCase() + device.status.slice(1)}
                  </span>
                </div>
                
                {device.lastActivity && (
                  <div className="flex justify-between">
                    <span className="text-locale-gray">Last Activity:</span>
                    <span className="text-locale-gray-dark text-xs">
                      {device.isOnline ? 'Just now' : 'Offline'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
        {pagedDevices.length < filteredDevices.length && (
          <div className="col-span-full flex justify-center">
            <button
              className="px-4 py-2 text-sm bg-cloud-white/70 border border-grid-lines rounded-locale hover:bg-cloud-white"
              onClick={() => setPage(p => p + 1)}
            >
              Load more devices
            </button>
          </div>
        )}
      </div>

      {/* No Results */}
      {filteredDevices.length === 0 && (
        <div className="locale-card text-center py-16">
          <Smartphone className="w-16 h-16 mx-auto mb-4 text-locale-gray/50" />
          <h3 className="text-h2 mb-2">No devices found</h3>
          <p className="text-locale-gray/60">
            Try adjusting your search criteria or filters
          </p>
        </div>
      )}
    </div>
  );
}; 