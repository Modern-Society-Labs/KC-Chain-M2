import React from 'react';
import { 
  HelpCircle, 
  Activity, 
  Smartphone, 
  BarChart3, 
  Clock, 
  Database,
  ExternalLink,
  Github,
  Server,
  Zap,
  Shield,
  Eye
} from 'lucide-react';

export const Settings: React.FC = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-h1">Help & Documentation</h1>
        <p className="text-body mt-2">
          Complete guide to understanding the L&#123;CORE&#125; IoT Dashboard and its components
        </p>
      </div>

      {/* Quick Links */}
      <div className="locale-card">
        <h2 className="text-h2 mb-4 flex items-center gap-2">
          <ExternalLink className="w-5 h-5" />
          Quick Links
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a 
            href="https://github.com/Modern-Society-Labs/lcore-iot-data" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-3 bg-locale-gray-light hover:bg-locale-gray rounded-lg transition-colors"
          >
            <Github className="w-5 h-5 text-locale-blue" />
            <div>
              <div className="font-medium text-locale-gray-dark">IoT Data Repository</div>
              <div className="text-sm text-locale-gray">Data Source and Methodology</div>
            </div>
          </a>
          
          <a 
            href="https://railway.com/project/2f6e747d-e792-44cf-9158-2b19c258467d/logs?environmentId=ca6d38f0-6867-4069-a509-7890e21e0fce" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-3 bg-locale-gray-light hover:bg-locale-gray rounded-lg transition-colors"
          >
            <Server className="w-5 h-5 text-accent-green" />
            <div>
              <div className="font-medium text-locale-gray-dark">Railway Deployment</div>
              <div className="text-sm text-locale-gray">Live L&#123;CORE&#125; Node Logs</div>
            </div>
          </a>
          
          <a 
            href="https://github.com/Modern-Society-Labs/lcore-node" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-3 bg-locale-gray-light hover:bg-locale-gray rounded-lg transition-colors"
          >
            <Github className="w-5 h-5 text-locale-blue" />
            <div>
              <div className="font-medium text-locale-gray-dark">Cartesi L&#123;CORE&#125;</div>
              <div className="text-sm text-locale-gray">Privacy Engine Backend</div>
            </div>
          </a>
          
          <a 
            href="https://explorer-1205614515668104.devnet.alchemy.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-3 bg-locale-gray-light hover:bg-locale-gray rounded-lg transition-colors"
          >
            <Database className="w-5 h-5 text-smart-city-teal" />
            <div>
              <div className="font-medium text-locale-gray-dark">Block Explorer</div>
              <div className="text-sm text-locale-gray">Devnet Blockchain Data</div>
            </div>
          </a>
        </div>
      </div>

      {/* Dashboard Components */}
      <div className="locale-card">
        <h2 className="text-h2 mb-6 flex items-center gap-2">
          <BarChart3 className="w-5 h-5" />
          Dashboard Components
        </h2>
        
        <div className="space-y-6">
          {/* Community Metrics */}
          <div className="border-l-4 border-smart-city-teal pl-4">
            <h3 className="font-semibold text-locale-gray-dark mb-2 flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Community Metrics
            </h3>
            <p className="text-sm text-locale-gray mb-3">
              Real-time statistics about the IoT network including device counts, total transactions, 
              and network activity. Data is fetched live from the blockchain via RPC calls.
            </p>
            <div className="text-xs text-locale-gray/80">
              <strong>Data Source:</strong> Ethereum RPC • <strong>Update Frequency:</strong> 30 seconds
            </div>
          </div>

          {/* Recent Activity */}
          <div className="border-l-4 border-accent-green pl-4">
            <h3 className="font-semibold text-locale-gray-dark mb-2 flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Recent Activity Timeline
            </h3>
            <p className="text-sm text-locale-gray mb-3">
              Live feed of blockchain transactions including both regular network activity and IoT device 
              submissions to the InputBox contract. Shows device-specific information when available.
            </p>
            <div className="text-xs text-locale-gray/80">
              <strong>Data Source:</strong> Direct blockchain RPC • <strong>Update Frequency:</strong> 30 seconds
            </div>
          </div>

          {/* Device Simulator */}
          <div className="border-l-4 border-locale-blue pl-4">
            <h3 className="font-semibold text-locale-gray-dark mb-2 flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Device Simulator Control
            </h3>
            <p className="text-sm text-locale-gray mb-3">
              Interface to control the IoT simulation service. Shows real-time status of devices 
              making actual blockchain transactions. Controls the Python FastAPI service running the simulation.
            </p>
            <div className="text-xs text-locale-gray/80">
              <strong>Data Source:</strong> FastAPI Simulation Service • <strong>Update Frequency:</strong> Real-time WebSocket
            </div>
          </div>
        </div>
      </div>

      {/* Device Registry */}
      <div className="locale-card">
        <h2 className="text-h2 mb-6 flex items-center gap-2">
          <Smartphone className="w-5 h-5" />
          Device Registry
        </h2>
        
        <div className="space-y-4">
          <p className="text-sm text-locale-gray">
            The Device Registry provides a comprehensive view of all 67 IoT devices in the network. 
            Each device has its own Ethereum wallet and submits real encrypted data to the blockchain.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="bg-locale-gray-light/50 p-3 rounded-lg">
              <h4 className="font-medium text-locale-gray-dark mb-2">Device Categories</h4>
              <ul className="space-y-1 text-locale-gray">
                <li>• Health Trackers</li>
                <li>• Retail Point-of-Sale</li>
                <li>• Network Infrastructure</li>
                <li>• Environmental Sensors</li>
                <li>• Weather Stations</li>
                <li>• Agricultural Monitors</li>
              </ul>
            </div>
            
            <div className="bg-locale-gray-light/50 p-3 rounded-lg">
              <h4 className="font-medium text-locale-gray-dark mb-2">Live Indicators</h4>
              <ul className="space-y-1 text-locale-gray">
                <li>• Online/Offline Status</li>
                <li>• Total InputBox Submissions</li>
                <li>• Last Activity Timestamp</li>
                <li>• Device Wallet Address</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Privacy & Security */}
      <div className="locale-card">
        <h2 className="text-h2 mb-6 flex items-center gap-2">
          <Shield className="w-5 h-5" />
          Privacy & Security Architecture
        </h2>
        
        <div className="space-y-4">
          <p className="text-sm text-locale-gray">
            The L&#123;CORE&#125; system implements privacy-preserving IoT data processing through Cartesi rollups 
            and cryptographic techniques.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-locale-gray-dark mb-3 flex items-center gap-2">
                <Eye className="w-4 h-4" />
                What You Can See
              </h4>
              <ul className="space-y-2 text-sm text-locale-gray">
                <li>• Device transaction metadata</li>
                <li>• Blockchain verification proofs</li>
                <li>• Network activity patterns</li>
                <li>• Device online/offline status</li>
                <li>• Transaction gas costs</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-locale-gray-dark mb-3 flex items-center gap-2">
                <Shield className="w-4 h-4" />
                What's Privacy-Protected
              </h4>
              <ul className="space-y-2 text-sm text-locale-gray">
                <li>• Actual sensor readings</li>
                <li>• User personal information</li>
                <li>• Location coordinates</li>
                <li>• Device-specific identifiers</li>
                <li>• Business analytics data</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="locale-card">
        <h2 className="text-h2 mb-6 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          System Health Indicators
        </h2>
        
        <div className="space-y-4">
          <p className="text-sm text-locale-gray">
            The header displays real-time status of key system components. All indicators should show "Online" 
            for optimal operation.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-2 bg-locale-gray-light/50 rounded">
                <Server className="w-4 h-4 text-accent-green" />
                <div>
                  <div className="font-medium text-sm">L&#123;CORE&#125; Node</div>
                  <div className="text-xs text-locale-gray">Cartesi execution environment</div>
                </div>
              </div>
              
              <div className="flex items-center gap-3 p-2 bg-locale-gray-light/50 rounded">
                <Database className="w-4 h-4 text-accent-green" />
                <div>
                  <div className="font-medium text-sm">GraphQL</div>
                  <div className="text-xs text-locale-gray">API query interface</div>
                </div>
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-2 bg-locale-gray-light/50 rounded">
                <Activity className="w-4 h-4 text-accent-green" />
                <div>
                  <div className="font-medium text-sm">Cartesi Machine</div>
                  <div className="text-xs text-locale-gray">Privacy computation layer</div>
                </div>
              </div>
              
              <div className="flex items-center gap-3 p-2 bg-locale-gray-light/50 rounded">
                <Zap className="w-4 h-4 text-accent-green" />
                <div>
                  <div className="font-medium text-sm">Locale Network</div>
                  <div className="text-xs text-locale-gray">IoT device connectivity</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Technical Details */}
      <div className="locale-card">
        <h2 className="text-h2 mb-6 flex items-center gap-2">
          <HelpCircle className="w-5 h-5" />
          Technical Implementation
        </h2>
        
        <div className="space-y-4 text-sm text-locale-gray">
          <div>
            <h4 className="font-medium text-locale-gray-dark mb-2">Blockchain Infrastructure</h4>
            <p className="mb-2">
              Built on Ethereum-compatible devnet with Alchemy RPC provider. All IoT data submissions 
              are verified on-chain through the InputBox contract at address:
            </p>
            <code className="bg-locale-gray-light p-2 rounded font-mono text-xs block">
              0xC1f612D9ad2270e31BF41fAdBb92f79B63649133
            </code>
          </div>
          
          <div>
            <h4 className="font-medium text-locale-gray-dark mb-2">Frontend Technology</h4>
            <p>
              React 18 + TypeScript + Tailwind CSS dashboard with real-time data fetching, 
              responsive design, and Vite for optimal development experience.
            </p>
          </div>
          
          <div>
            <h4 className="font-medium text-locale-gray-dark mb-2">Privacy Engine</h4>
            <p>
              Cartesi rollups provide off-chain computation with on-chain verification, 
              enabling complex privacy-preserving operations on encrypted IoT data while 
              maintaining blockchain security guarantees.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}; 