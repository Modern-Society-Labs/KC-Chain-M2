import React from 'react';
import { Users, TrendingUp, Clock, Activity, Zap } from 'lucide-react';
import { useSimulationService } from '../../hooks/useSimulationService';

export const CommunityMetrics: React.FC = () => {
  const { status, devices, connected } = useSimulationService();

  const calculateMetrics = () => {
    const domainsActive = new Set(devices.map(d => d.domain)).size;
    
    const dataPointsPerHour = status.uptime_seconds > 0 
      ? Math.round(status.total_submissions * (3600 / status.uptime_seconds))
      : 0;

    // Calculate node uptime in hours
    const uptimeHours = (status.uptime_seconds / 3600).toFixed(1);
    
    // Device to owner ratio (assuming 55 owners from wallet mapping)
    const deviceOwnerRatio = status.devices_active > 0 ? (status.devices_active / 55).toFixed(2) : '0.00';

    return {
      activeDevices: status.devices_active.toString(),
      dataPointsPerHour: dataPointsPerHour.toString(),
      nodeUptime: `${uptimeHours}h`,
      deviceOwnerRatio: deviceOwnerRatio,
      domainsActive
    };
  };

  const metrics_data = calculateMetrics();

  const metrics = [
    {
      title: 'Active Devices',
      value: metrics_data.activeDevices,
      change: connected ? '+Live' : 'Offline',
      icon: Users,
      color: 'text-smart-city-teal'
    },
    {
      title: 'Data Points/Hour',
      value: metrics_data.dataPointsPerHour,
      change: status.running && !status.paused ? '+Real-time' : 'Paused',
      icon: TrendingUp,
      color: 'text-accent-lime'
    },
    {
      title: 'Node Uptime',
      value: metrics_data.nodeUptime,
      change: `${metrics_data.domainsActive} domains`,
      icon: Clock,
      color: 'text-locale-blue'
    },
    {
      title: 'Device/Owner Ratio',
      value: metrics_data.deviceOwnerRatio,
      change: '55 total owners',
      icon: Users,
      color: 'text-warm-amber'
    }
  ];

  return (
    <div className="locale-card">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-locale-gradient rounded-lg flex items-center justify-center">
          <Zap className="w-5 h-5 text-white" />
        </div>
        <h3 className="text-h2">Live Community Metrics</h3>
        <div className="flex items-center gap-2 ml-auto">
          <Activity className={`w-4 h-4 ${connected && status.running && !status.paused ? 'text-accent-green animate-pulse' : 'text-urban-grey'}`} />
          <span className="text-sm text-urban-grey">
            {connected && status.running && !status.paused ? 'Live' : 'Offline'}
          </span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric) => {
          const IconComponent = metric.icon;
          return (
            <div key={metric.title} className="text-center p-4 bg-cloud-white/50 rounded-locale">
              <IconComponent className={`w-8 h-8 mx-auto mb-2 ${metric.color}`} />
              <div className="text-2xl font-bold text-urban-grey mb-1">{metric.value}</div>
              <div className="text-sm text-urban-grey/60 mb-1">{metric.title}</div>
              <div className="text-xs text-accent-lime">{metric.change}</div>
            </div>
          );
        })}
      </div>
      
      {status.running && connected && !status.paused && (
        <div className="mt-4 p-3 bg-accent-lime/10 rounded-locale">
          <div className="text-sm text-accent-lime font-medium">
            📡 Live simulation active
          </div>
        </div>
      )}
    </div>
  );
}; 