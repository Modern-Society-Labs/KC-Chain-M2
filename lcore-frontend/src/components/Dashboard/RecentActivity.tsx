import React, { useState, useEffect, useCallback } from 'react';
import { Clock, ExternalLink, CheckCircle, AlertCircle, Hash, RefreshCw } from 'lucide-react';
import { kcChainService, type RecentActivity as RecentActivityData } from '../../services/kcChainService';

export const RecentActivity: React.FC = () => {
  const [activities, setActivities] = useState<RecentActivityData[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchActivity = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      
      console.log('🔄 Fetching recent activity for real-time updates...');
      const data = await kcChainService.getRecentActivity();
      setActivities(data);
      setError(null);
      setLastRefresh(new Date());
      
      console.log(`✅ Updated Recent Activity: ${data.length} items`);
    } catch (err) {
      setError('Failed to load activity');
      console.error('Error fetching recent activity:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    // Initial fetch
    fetchActivity();

    // Set up real-time polling every 30 seconds to catch new IoT transactions
    const pollInterval = setInterval(() => {
      console.log('⏰ Auto-refreshing Recent Activity for real-time IoT data...');
      fetchActivity(true);
    }, 30000); // 30 seconds

    // Cleanup interval on unmount
    return () => {
      clearInterval(pollInterval);
      console.log('🛑 Stopped Recent Activity polling');
    };
  }, [fetchActivity]);

  // Manual refresh function
  const handleManualRefresh = () => {
    console.log('🔄 Manual refresh triggered');
    fetchActivity(true);
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date().getTime();
    const time = new Date(timestamp).getTime();
    const diffInSeconds = Math.floor((now - time) / 1000);
    
    if (diffInSeconds < 60) return `${diffInSeconds}s ago`;
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-accent-lime" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-muted-coral" />;
      default:
        return <Clock className="w-4 h-4 text-warm-amber" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'transaction':
        return 'text-smart-city-teal';
      case 'block':
        return 'text-locale-blue';
      case 'contract':
        return 'text-warm-amber';
      default:
        return 'text-urban-grey';
    }
  };

  if (loading) {
    return (
      <div className="locale-card">
        <div className="flex items-center gap-3 mb-6">
          <Clock className="w-6 h-6 text-urban-grey" />
          <h3 className="text-h2">Recent Activity</h3>
        </div>
        
        <div className="text-center py-8 text-urban-grey/60">
          <div className="w-6 h-6 border-2 border-urban-grey border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
          <p>Loading blockchain activity...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="locale-card">
        <div className="flex items-center gap-3 mb-6">
          <Clock className="w-6 h-6 text-urban-grey" />
          <h3 className="text-h2">Recent Activity</h3>
        </div>
        
        <div className="text-center py-8 text-muted-coral">
          <AlertCircle className="w-8 h-8 mx-auto mb-2" />
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="locale-card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Clock className="w-6 h-6 text-urban-grey" />
          <h3 className="text-h2">Recent Activity</h3>
          <span className="text-sm text-urban-grey/60 bg-urban-grey/10 px-2 py-1 rounded">
            {activities.length} items
          </span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-urban-grey/60">
            <div className={`w-2 h-2 rounded-full ${refreshing ? 'bg-warm-amber animate-pulse' : 'bg-accent-lime animate-pulse'}`}></div>
            <span>{refreshing ? 'Updating...' : 'Live from Locale Network'}</span>
          </div>
          <button
            onClick={handleManualRefresh}
            disabled={refreshing}
            className="p-1 text-urban-grey/60 hover:text-urban-grey transition-colors disabled:opacity-50"
            title={`Last updated: ${lastRefresh.toLocaleTimeString()}`}
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
      
      <div className="space-y-3 max-h-80 overflow-y-auto">
        {activities.map((activity) => (
          <div key={activity.id} className="flex items-start gap-3 p-3 bg-cloud-white/30 rounded-locale hover:bg-cloud-white/50 transition-colors">
            <div className="flex-shrink-0 mt-1">
              {getStatusIcon(activity.status)}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-sm font-medium ${getTypeColor(activity.type)}`}>
                  {activity.title}
                </span>
                <span className="text-xs text-urban-grey/60">
                  {formatTimeAgo(activity.timestamp)}
                </span>
              </div>
              
              <p className="text-xs text-urban-grey/70 mb-2">
                {activity.description}
              </p>
              
              <div className="flex items-center gap-2">
                <Hash className="w-3 h-3 text-urban-grey/50" />
                <span className="text-xs font-mono text-urban-grey/60">
                  {activity.hash ? `${activity.hash.slice(0, 10)}...${activity.hash.slice(-8)}` : 'Loading...'}
                </span>
                {activity.hash && activity.explorerUrl && (
                  <a
                    href={activity.explorerUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-auto text-locale-blue hover:text-locale-blue-dark transition-colors"
                    title="View on Locale Network Explorer"
                  >
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {activities.length === 0 && (
          <div className="text-center py-8 text-urban-grey/60">
            <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>No recent activity</p>
          </div>
        )}
      </div>
      
      <div className="mt-4 pt-4 border-t border-grid-lines">
        <a
          href="https://explorer-1205614515668104.devnet.alchemy.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 w-full py-2 text-sm text-locale-blue hover:text-locale-blue-dark transition-colors"
        >
          <span>View all activity</span>
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
}; 