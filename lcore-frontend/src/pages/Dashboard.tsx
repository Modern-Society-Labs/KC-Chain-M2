import React from 'react';
import { CommunityMetrics } from '../components/Dashboard/CommunityMetrics';
import { DeviceSimulator } from '../components/Dashboard/DeviceSimulator';
import { RecentActivity } from '../components/Dashboard/RecentActivity';

export const Dashboard: React.FC = () => {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="mb-8">
        <div>
          <h1 className="text-h1 mb-3">L&#123;CORE&#125; IoT Dashboard</h1>
          <p className="text-body">
            Real-time monitoring of 67 IoT simulated devices submitting encrypted data to the Cartesi L&#123;CORE&#125; node. 
            All sensitive device data is privacy-protected through zero-knowledge proofs and cryptographic verification 
            within the Cartesi execution layer, ensuring data utility while preserving user privacy. 
            <br />
            <br />
            <span className="text-sm text-locale-gray-dark">
              <i>Note: This is a demo environment. The data is simulated but the backend and on-chain functions are real.</i>
            </span>
          </p>
        </div>
      </div>
      
      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
        {/* Primary Content - Full width on mobile, spans 2 cols on large screens */}
        <div className="lg:col-span-2 space-y-4 sm:space-y-6 lg:space-y-8">
          {/* Live Community Metrics (with lightning icon from RealTimeDataFlow) */}
          <CommunityMetrics />
          
          {/* Recent Activity (moved up) */}
          <RecentActivity />
        </div>
        
        {/* Sidebar Content - Stack on mobile, sidebar on larger screens */}
        <div className="space-y-4 sm:space-y-6 lg:space-y-8">
          {/* Device Simulator */}
          <DeviceSimulator />
        </div>
      </div>
    </div>
  );
}; 