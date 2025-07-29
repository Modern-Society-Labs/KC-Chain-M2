import React from 'react';
import { Activity, Server, Database, Wifi } from 'lucide-react';

export const SystemHealth: React.FC = () => {
  const healthItems = [
    { name: 'LCore Node', status: 'online', icon: Server, color: 'text-accent-lime' },
    { name: 'GraphQL', status: 'online', icon: Database, color: 'text-accent-lime' },
    { name: 'Locale Network', status: 'online', icon: Wifi, color: 'text-accent-lime' },
    { name: 'Cartesi Machine', status: 'online', icon: Activity, color: 'text-accent-lime' }
  ];

  return (
    <div className="locale-card">
      <div className="flex items-center gap-3 mb-6">
        <Activity className="w-6 h-6 text-accent-lime" />
        <h3 className="text-h2">System Health</h3>
      </div>

      <div className="space-y-3">
        {healthItems.map((item) => {
          const IconComponent = item.icon;
          return (
            <div key={item.name} className="flex items-center gap-3 p-3 bg-cloud-white/50 rounded-locale">
              <IconComponent className={`w-4 h-4 ${item.color}`} />
              <span className="flex-1 text-sm text-urban-grey">{item.name}</span>
              <div className="w-2 h-2 bg-accent-lime rounded-full"></div>
            </div>
          );
        })}
      </div>
    </div>
  );
}; 