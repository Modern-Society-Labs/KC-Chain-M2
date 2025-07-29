import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Smartphone, 
  HelpCircle,
  Shield,
  BarChart3,
  ExternalLink,
  Github,
  Mail,
  Globe
} from 'lucide-react';

const navigationItems = [
  {
    name: 'Dashboard',
    path: '/',
    icon: Home
  },
  {
    name: 'Devices',
    path: '/devices',
    icon: Smartphone
  },
  {
    name: 'Help',
    path: '/settings',
    icon: HelpCircle
  }
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  return (
    <div className={`
      w-64 bg-white border-r border-locale-gray-light flex flex-col
      fixed inset-y-0 left-0 z-50 transform transition-transform duration-300 ease-in-out
      ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
    `}>
      {/* Logo & Branding */}
      <div className="p-6 border-b border-locale-gray-light">
        <div className="flex items-center gap-3">
          <img 
            src="/Locale Logo.png" 
            alt="Locale Logo" 
            className="w-10 h-10 object-contain"
          />
          <div>
            <h1 className="text-xl font-bold text-locale-gray-dark">L&#123;CORE&#125;</h1>
            <p className="text-locale-gray text-sm">City-Chain Dashboard</p>
          </div>
        </div>
      </div>
      
      {/* Privacy Indicator */}
      <div className="p-4 border-b border-locale-gray-light">
        <div className="flex items-center gap-2 text-sm">
          <Shield className="w-4 h-4 text-accent-green" />
          <span className="text-accent-green font-medium">Privacy Protected</span>
        </div>
      </div>
      
      {/* Navigation Menu */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigationItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `nav-item ${isActive ? 'nav-item-active' : ''} group`
                  }
                  end={item.path === '/'}
                  onClick={() => {
                    // Close mobile menu when navigation item is clicked
                    if (onClose && window.innerWidth < 1024) {
                      onClose();
                    }
                  }}
                >
                  <IconComponent className="w-5 h-5" />
                  <div className="flex-1">
                    <div className="font-medium">{item.name}</div>
                  </div>
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>
      
      {/* Social Media Links */}
      <div className="p-4 border-t border-locale-gray-light">
        <h3 className="text-sm font-medium text-locale-gray-dark mb-3">Connect</h3>
        <div className="grid grid-cols-2 gap-2">
          <a
            href="https://www.locale.cash"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 p-2 text-locale-gray hover:text-locale-blue hover:bg-locale-gray-light rounded-lg transition-colors text-xs"
          >
            <Globe className="w-3 h-3" />
            <span>Website</span>
            <ExternalLink className="w-2 h-2 ml-auto" />
          </a>
          
          <a
            href="https://www.x.com/localenet"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 p-2 text-locale-gray hover:text-locale-blue hover:bg-locale-gray-light rounded-lg transition-colors text-xs"
          >
            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
            </svg>
            <span>X</span>
            <ExternalLink className="w-2 h-2 ml-auto" />
          </a>
          
          <a
            href="https://www.github.com/modern-society-labs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 p-2 text-locale-gray hover:text-locale-blue hover:bg-locale-gray-light rounded-lg transition-colors text-xs"
          >
            <Github className="w-3 h-3" />
            <span>GitHub</span>
            <ExternalLink className="w-2 h-2 ml-auto" />
          </a>
          
          <a
            href="mailto:hello@modernsociety.xyz"
            className="flex items-center gap-2 p-2 text-locale-gray hover:text-locale-blue hover:bg-locale-gray-light rounded-lg transition-colors text-xs"
          >
            <Mail className="w-3 h-3" />
            <span>Email</span>
            <ExternalLink className="w-2 h-2 ml-auto" />
          </a>
        </div>
      </div>
      
      {/* Network Status */}
      <div className="p-4 border-t border-locale-gray-light">
        <div className="flex items-center gap-2 text-sm">

          <span className="text-locale-gray-dark font-medium">Locale Network</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-locale-gray mt-1">
          <div className="w-2 h-2 bg-accent-green rounded-full animate-pulse"></div>
          <span>lcore-node • Online</span>
        </div>
      </div>
    </div>
  );
}; 