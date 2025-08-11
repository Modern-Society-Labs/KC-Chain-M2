import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  Database, 
  Eye, 
  Filter,
  Download,
  Zap,
  Lock,
  Unlock,
  RefreshCw,
  BarChart3,
  Users,
  MapPin
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { 
  dataExplorerService,
  type InputRecord,
  type DecryptedPayload,
  type AggregatedData
} from '../services/dataExplorerService';



const DEMO_DEVICE_TYPES = [
  { id: 'environmental', name: 'Environmental Sensors', icon: '🌡️', color: 'text-green-400' },
  { id: 'health', name: 'Health Trackers', icon: '❤️', color: 'text-red-400' },
  { id: 'retail', name: 'Retail Analytics', icon: '🛒', color: 'text-blue-400' },
  { id: 'network', name: 'Network Monitoring', icon: '📡', color: 'text-purple-400' },
  { id: 'weather', name: 'Weather Stations', icon: '⛅', color: 'text-cyan-400' },
  { id: 'agricultural', name: 'Agricultural Sensors', icon: '🌾', color: 'text-yellow-400' },
];

export const DataExplorer: React.FC = () => {
  const [inputRecords, setInputRecords] = useState<InputRecord[]>([]);
  const [decryptedData, setDecryptedData] = useState<DecryptedPayload[]>([]);
  const [aggregatedData, setAggregatedData] = useState<AggregatedData[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDeviceType, setSelectedDeviceType] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'raw' | 'decrypted' | 'aggregated'>('decrypted');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchInputRecords = async (deviceType?: string) => {
    setLoading(true);
    try {
      const records = await dataExplorerService.fetchInputRecords(deviceType, 50);
      setInputRecords(records);
      toast.success(`Loaded ${records.length} input records`);
    } catch (error) {
      console.error('Failed to fetch input records:', error);
      toast.error('Failed to load input records');
    } finally {
      setLoading(false);
    }
  };

  const decryptInputData = async (deviceType?: string) => {
    setLoading(true);
    try {
      // First fetch records if we don't have any
      let recordsToDecrypt = inputRecords;
      if (recordsToDecrypt.length === 0) {
        recordsToDecrypt = await dataExplorerService.fetchInputRecords(deviceType, 50);
        setInputRecords(recordsToDecrypt);
      }
      
      // Decrypt the records
      const decrypted = await dataExplorerService.decryptInputData(recordsToDecrypt);
      setDecryptedData(decrypted);
      toast.success(`Decrypted ${decrypted.length} sensor readings`);
    } catch (error) {
      console.error('Failed to decrypt data:', error);
      toast.error('Failed to decrypt sensor data');
    } finally {
      setLoading(false);
    }
  };

  const generateAggregatedReport = async () => {
    setLoading(true);
    try {
      // First ensure we have decrypted data
      let dataToAggregate = decryptedData;
      if (dataToAggregate.length === 0) {
        // Fetch and decrypt data first
        const records = await dataExplorerService.fetchInputRecords(selectedDeviceType, 50);
        setInputRecords(records);
        dataToAggregate = await dataExplorerService.decryptInputData(records);
        setDecryptedData(dataToAggregate);
      }
      
      // Generate aggregated report
      const aggregated = await dataExplorerService.generateAggregatedReport(dataToAggregate);
      setAggregatedData(aggregated);
      toast.success('Generated aggregated analytics report');
    } catch (error) {
      console.error('Failed to generate report:', error);
      toast.error('Failed to generate analytics');
    } finally {
      setLoading(false);
    }
  };

  const filteredData = decryptedData.filter(item => {
    const matchesSearch = searchQuery === '' || 
      item.device_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.domain.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesDeviceType = selectedDeviceType === 'all' || item.domain === selectedDeviceType;
    
    return matchesSearch && matchesDeviceType;
  });

  return (
    <div className="min-h-screen bg-locale-bg p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-4">
            <Database className="w-8 h-8 text-accent-cyan" />
            <h1 className="text-3xl font-bold text-locale-blue">Data Explorer</h1>
          </div>
          <p className="text-urban-grey/70">
            Query and decrypt IoT sensor data from the Locale Network
          </p>
        </motion.div>

        {/* Control Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="locale-card mb-8"
        >
          <div className="flex flex-wrap gap-4 items-center justify-between">
            {/* Device Type Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-slate-400" />
              <select
                value={selectedDeviceType}
                onChange={(e) => setSelectedDeviceType(e.target.value)}
                className="select-field"
              >
                <option value="all">All Device Types</option>
                {DEMO_DEVICE_TYPES.map(type => (
                  <option key={type.id} value={type.id}>
                    {type.icon} {type.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Search */}
            <div className="flex items-center gap-2 flex-1 max-w-md">
              <Search className="w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search devices or domains..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-field flex-1"
              />
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center gap-2 bg-cloud-white/50 rounded-locale p-1">
              {[
                { key: 'raw', label: 'Raw', icon: Database, disabled: false },
                { key: 'decrypted', label: 'Decrypted', icon: Unlock, disabled: false },
                { key: 'aggregated', label: 'Analytics', icon: BarChart3, disabled: true }
              ].map(({ key, label, icon: Icon, disabled }) => (
                <button
                  key={key}
                  onClick={() => !disabled && setViewMode(key as any)}
                  disabled={disabled}
                  className={`flex items-center gap-2 px-3 py-2 rounded transition-colors ${
                    viewMode === key
                      ? 'bg-locale-blue text-white'
                      : 'text-urban-grey hover:text-locale-blue'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* One-Click Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
        >
          <button
            onClick={() => fetchInputRecords(selectedDeviceType)}
            disabled={loading}
            className="flex items-center justify-center gap-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <Database className="w-5 h-5" />
            Load Raw Inputs
            {loading && <RefreshCw className="w-4 h-4 animate-spin" />}
          </button>

          <button
            onClick={() => decryptInputData(selectedDeviceType)}
            disabled={loading}
            className="flex items-center justify-center gap-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <Unlock className="w-5 h-5" />
            Decrypt Sensor Data
            {loading && <RefreshCw className="w-4 h-4 animate-spin" />}
          </button>

          <button
            onClick={generateAggregatedReport}
            disabled={true}
            className="flex items-center justify-center gap-3 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <BarChart3 className="w-5 h-5" />
            Generate Analytics
            {loading && <RefreshCw className="w-4 h-4 animate-spin" />}
          </button>
        </motion.div>

        {/* Data Display */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="locale-card"
        >
          {viewMode === 'raw' && (
            <div>
              <h3 className="text-xl font-semibold text-locale-blue mb-4 flex items-center gap-2">
                <Lock className="w-5 h-5 text-red-400" />
                Raw Encrypted Inputs ({inputRecords.length})
              </h3>
              <div className="space-y-3">
                {inputRecords.map((record) => (
                  <div key={record.index} className="locale-card bg-cloud-white/80 border border-grid-lines p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-smart-city-teal font-mono">#{record.index}</span>
                      <span className="text-urban-grey/60 text-sm">{record.timestamp}</span>
                    </div>
                    <div className="text-sm text-urban-grey">
                      <p><strong>Device:</strong> {record.payload.device_id}</p>
                      <p><strong>Status:</strong> 
                        <span className={`ml-2 px-2 py-1 rounded text-xs ${
                          record.status === 'Processed' 
                            ? 'bg-accent-lime/20 text-accent-lime' 
                            : 'bg-warm-amber/20 text-warm-amber'
                        }`}>
                          {record.status}
                        </span>
                      </p>
                      <p className="mt-2 font-mono text-xs text-urban-grey/60 truncate">
                        {record.payload.encrypted_payload}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {viewMode === 'decrypted' && (
            <div>
              <h3 className="text-xl font-semibold text-locale-blue mb-4 flex items-center gap-2">
                <Unlock className="w-5 h-5 text-green-400" />
                Decrypted Sensor Readings ({filteredData.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredData.map((data, index) => {
                  const deviceType = DEMO_DEVICE_TYPES.find(t => t.id === data.domain);
                  return (
                    <div key={index} className="locale-card bg-cloud-white/80 border border-grid-lines p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <span className={`text-2xl ${deviceType?.color}`}>
                          {deviceType?.icon || '📊'}
                        </span>
                        <div>
                          <h4 className="text-locale-blue font-medium">{deviceType?.name}</h4>
                          <p className="text-urban-grey/60 text-xs font-mono">
                            {data.device_id.replace('did:lcore:', '')}
                          </p>
                        </div>
                      </div>
                      
                      <div className="space-y-2 text-sm">
                        {data.temperature && (
                          <div className="flex justify-between">
                            <span className="text-urban-grey/70">Temperature:</span>
                            <span className="text-urban-grey">{data.temperature}°C</span>
                          </div>
                        )}
                        {data.humidity && (
                          <div className="flex justify-between">
                            <span className="text-urban-grey/70">Humidity:</span>
                            <span className="text-urban-grey">{data.humidity}%</span>
                          </div>
                        )}
                        {data.transaction_value && (
                          <div className="flex justify-between">
                            <span className="text-urban-grey/70">Transaction:</span>
                            <span className="text-urban-grey">${data.transaction_value}</span>
                          </div>
                        )}
                        <div className="flex justify-between pt-2 border-t border-grid-lines">
                          <span className="text-urban-grey/70">Privacy Score:</span>
                          <span className="text-accent-lime">{data.privacy_metadata.privacy_score}%</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {viewMode === 'aggregated' && (
            <div>
              <h3 className="text-xl font-semibold text-locale-blue mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-accent-purple" />
                Aggregated Analytics ({aggregatedData.length} domains)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {aggregatedData.map((data, index) => {
                  const deviceType = DEMO_DEVICE_TYPES.find(t => t.id === data.domain);
                  return (
                    <div key={index} className="locale-card bg-cloud-white/80 border border-grid-lines p-6">
                      <div className="flex items-center gap-3 mb-4">
                        <span className={`text-3xl ${deviceType?.color}`}>
                          {deviceType?.icon || '📊'}
                        </span>
                        <div>
                          <h4 className="text-locale-blue font-semibold text-lg">{deviceType?.name}</h4>
                          <p className="text-urban-grey/70">{data.device_count} devices, {data.total_readings} readings</p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        {data.avg_temperature && (
                          <div className="text-center">
                            <p className="text-2xl font-bold text-locale-blue">{data.avg_temperature}°C</p>
                            <p className="text-urban-grey/70 text-sm">Avg Temperature</p>
                          </div>
                        )}
                        {data.avg_transaction_value && (
                          <div className="text-center">
                            <p className="text-2xl font-bold text-smart-city-teal">${data.avg_transaction_value}</p>
                            <p className="text-urban-grey/70 text-sm">Avg Transaction</p>
                          </div>
                        )}
                        {data.avg_signal_strength && (
                          <div className="text-center">
                            <p className="text-2xl font-bold text-warm-amber">{data.avg_signal_strength}dBm</p>
                            <p className="text-urban-grey/70 text-sm">Avg Signal</p>
                          </div>
                        )}
                        <div className="text-center">
                          <p className="text-2xl font-bold text-accent-lime">{data.privacy_score}%</p>
                          <p className="text-urban-grey/70 text-sm">Privacy Score</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Empty State */}
          {((viewMode === 'raw' && inputRecords.length === 0) ||
            (viewMode === 'decrypted' && decryptedData.length === 0) ||
            (viewMode === 'aggregated' && aggregatedData.length === 0)) && (
            <div className="text-center py-12">
              <Eye className="w-16 h-16 text-urban-grey/40 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-urban-grey mb-2">No Data Available</h3>
              <p className="text-urban-grey/70">
                Click one of the action buttons above to load and explore IoT data
              </p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};