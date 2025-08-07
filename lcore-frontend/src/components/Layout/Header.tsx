import React from 'react';
import { 
  Activity, 
  Server,
  Database,
  Wifi,
  Menu
} from 'lucide-react';
import { useAccount } from 'wagmi';
import { modal } from '../../config/wallet';

interface HeaderProps {
  onMenuToggle?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onMenuToggle }) => {
  const { address, isConnected } = useAccount();

  const handleWalletConnect = () => {
    modal.open();
  };

  return (
    <header className="bg-white border-b border-locale-gray-light px-4 sm:px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Mobile Menu Button & Title */}
        <div className="flex items-center gap-4">
          {/* Mobile Hamburger Menu */}
          <button
            onClick={onMenuToggle}
            className="lg:hidden p-2 text-locale-gray hover:text-locale-blue transition-colors"
          >
            <Menu className="w-6 h-6" />
          </button>
          
          <div>
            <div className="flex items-center gap-2 sm:gap-4">
              <div className="flex items-center gap-2 text-sm">
                <div className="w-2 h-2 bg-accent-green rounded-full animate-pulse"></div>
                <span className="text-locale-gray">Live Data</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* System Health Status - Hidden on mobile, visible on desktop */}
        <div className="hidden md:flex items-center gap-3 lg:gap-4">
          {/* LCore Node */}
          <div className="flex items-center gap-1.5">
            <Server className="w-4 h-4 text-accent-green" />
            <div className="text-xs lg:text-sm">
              <div className="font-medium text-locale-gray-dark">LCore Node</div>
              <div className="text-xs text-accent-green">Online</div>
            </div>
          </div>
          
          {/* GraphQL */}
          <div className="flex items-center gap-1.5">
            <Database className="w-4 h-4 text-accent-green" />
            <div className="text-xs lg:text-sm">
              <div className="font-medium text-locale-gray-dark">GraphQL</div>
              <div className="text-xs text-accent-green">Online</div>
            </div>
          </div>
          
          {/* Locale Network */}
          <div className="flex items-center gap-1.5">
            <Wifi className="w-4 h-4 text-accent-green" />
            <div className="text-xs lg:text-sm">
              <div className="font-medium text-locale-gray-dark">Locale Network</div>
              <div className="text-xs text-accent-green">Online</div>
            </div>
          </div>
          
          {/* Cartesi Machine */}
          <div className="flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-accent-green" />
            <div className="text-xs lg:text-sm">
              <div className="font-medium text-locale-gray-dark">Cartesi Machine</div>
              <div className="text-xs text-accent-green">Online</div>
            </div>
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Wallet Connect */}
          <w3m-button />
        </div>
      </div>
    </header>
  );
}; 