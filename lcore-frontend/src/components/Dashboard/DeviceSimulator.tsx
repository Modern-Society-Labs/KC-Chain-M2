import React, { useState } from 'react';
import { 
  Play, 
  Square, 
  Radio, 
  Settings,
  Activity,
  Clock,
  Zap,
  Pause,
  RotateCcw
} from 'lucide-react';
import { useSimulationService } from '../../hooks/useSimulationService';

export const DeviceSimulator: React.FC = () => {
  const {
    status,
    devices,
    connected,
    interval,
    startSimulation,
    stopSimulation,
    pauseSimulation,
    resumeSimulation,
    restartSimulation,
    updateInterval
  } = useSimulationService();

  const [intervalInput, setIntervalInput] = useState(interval.toString());
  const [updating, setUpdating] = useState(false);

  const handleStart = async () => {
    setUpdating(true);
    try {
      await startSimulation();
    } catch (error) {
      console.error('Error starting simulation:', error);
    } finally {
      setUpdating(false);
    }
  };

  const handleStop = async () => {
    setUpdating(true);
    try {
      await stopSimulation();
    } catch (error) {
      console.error('Error stopping simulation:', error);
    } finally {
      setUpdating(false);
    }
  };

  const handlePause = async () => {
    setUpdating(true);
    try {
      await pauseSimulation();
    } catch (error) {
      console.error('Error pausing simulation:', error);
    } finally {
      setUpdating(false);
    }
  };

  const handleResume = async () => {
    setUpdating(true);
    try {
      await resumeSimulation();
    } catch (error) {
      console.error('Error resuming simulation:', error);
    } finally {
      setUpdating(false);
    }
  };

  const handleRestart = async () => {
    setUpdating(true);
    try {
      await restartSimulation();
    } catch (error) {
      console.error('Error restarting simulation:', error);
    } finally {
      setUpdating(false);
    }
  };

  const handleIntervalUpdate = async () => {
    const newInterval = parseFloat(intervalInput);
    if (isNaN(newInterval) || newInterval < 20 || newInterval > 300) {
      alert('Interval must be between 20 and 300 seconds (20s - 5min for 3-day simulation)');
      return;
    }

    setUpdating(true);
    try {
      await updateInterval(newInterval);
    } catch (error) {
      console.error('Error updating interval:', error);
    } finally {
      setUpdating(false);
    }
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const getStatusColor = () => {
    if (!connected) return 'text-urban-grey';
    if (status.paused) return 'text-warm-amber';
    return status.running ? 'text-accent-lime' : 'text-urban-grey';
  };

  const getStatusText = () => {
    if (!connected) return 'Service Offline';
    if (status.paused) return 'Paused';
    return status.running ? 'Running' : 'Stopped';
  };

  // Update interval input when interval changes
  React.useEffect(() => {
    setIntervalInput(interval.toString());
  }, [interval]);

  const renderControls = () => {
    if (!status.running) {
      // Show start button when not running
      return (
        <button
          onClick={handleStart}
          disabled={updating || !connected}
          className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all bg-locale-blue text-white hover:bg-locale-blue-dark ${(updating || !connected) ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {updating ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Starting...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Start Simulation
            </>
          )}
        </button>
      );
    }

    // Show control panel when running (paused or active)
    return (
      <div className="space-y-3">
        <div className="grid grid-cols-3 gap-2">
          {status.paused ? (
            <button
              onClick={handleResume}
              disabled={updating}
              className={`flex items-center justify-center gap-1 px-2 py-2 rounded-lg font-medium transition-all bg-accent-green text-white hover:bg-accent-green/80 ${updating ? 'opacity-50 cursor-not-allowed' : ''} text-sm`}
            >
              <Play className="w-4 h-4" />
              Resume
            </button>
          ) : (
            <button
              onClick={handlePause}
              disabled={updating}
              className={`flex items-center justify-center gap-1 px-2 py-2 rounded-lg font-medium transition-all bg-accent-yellow text-white hover:bg-accent-yellow/80 ${updating ? 'opacity-50 cursor-not-allowed' : ''} text-sm`}
            >
              <Pause className="w-4 h-4" />
              Pause
            </button>
          )}
          
          <button
            onClick={handleRestart}
            disabled={updating}
            className={`flex items-center justify-center gap-1 px-2 py-2 rounded-lg font-medium transition-all bg-locale-blue text-white hover:bg-locale-blue-dark ${updating ? 'opacity-50 cursor-not-allowed' : ''} text-sm`}
          >
            <RotateCcw className="w-4 h-4" />
            Restart
          </button>
          
          <button
            onClick={handleStop}
            disabled={updating}
            className={`flex items-center justify-center gap-1 px-2 py-2 rounded-lg font-medium transition-all bg-status-error text-white hover:bg-status-error/80 ${updating ? 'opacity-50 cursor-not-allowed' : ''} text-sm`}
          >
            <Square className="w-4 h-4" />
            Stop
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="locale-card">
      <div className="flex items-center gap-3 mb-6">
        <Radio className="w-6 h-6 text-smart-city-teal" />
        <h3 className="text-h2">Device Simulator</h3>
        <div className={`w-2 h-2 rounded-full ${connected ? 'bg-accent-lime animate-pulse' : 'bg-urban-grey'}`}></div>
      </div>

      {/* Connection Status */}
      <div className="bg-cloud-white/50 rounded-locale p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className={`w-4 h-4 ${getStatusColor()}`} />
            <span className="font-medium">{getStatusText()}</span>
          </div>
          {status.running && (
            <div className="flex items-center gap-2 text-sm text-urban-grey/60">
              <Clock className="w-3 h-3" />
              <span>{formatUptime(status.uptime_seconds)}</span>
            </div>
          )}
        </div>
        
        {connected && (
          <div className="mt-2 text-xs text-urban-grey/60">
            🔗 Real-time L{'{CORE}'} Integration: {status.total_submissions} submissions
          </div>
        )}
      </div>

      {/* Interval Configuration */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-urban-grey mb-2">
            Submission Interval (seconds)
          </label>
          <div className="flex gap-2">
            <input
              type="number"
              min="20"
              max="300"
              step="5"
              value={intervalInput}
              onChange={(e) => setIntervalInput(e.target.value)}
              className="input-field flex-1"
              disabled={updating}
            />
            <button
              onClick={handleIntervalUpdate}
              disabled={updating || parseFloat(intervalInput) === interval}
              className="btn-secondary px-3"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
          <p className="text-xs text-urban-grey/60 mt-1">
            Current: {interval}s per device (20s - 5min range for 3-day simulation)
          </p>
        </div>

        {/* Control Buttons */}
        {renderControls()}
      </div>

      {/* Real-time Statistics */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center p-3 bg-cloud-white/50 rounded-locale">
          <div className="text-lg font-bold text-smart-city-teal">
            {status.devices_active}
          </div>
          <div className="text-xs text-urban-grey/60">Active Devices</div>
        </div>
        
        <div className="text-center p-3 bg-cloud-white/50 rounded-locale">
          <div className="text-lg font-bold text-accent-lime">
            {status.total_submissions}
          </div>
          <div className="text-xs text-urban-grey/60">Total Submissions</div>
        </div>
        
        <div className="text-center p-3 bg-cloud-white/50 rounded-locale">
          <div className="text-lg font-bold text-locale-blue">
            {status.successful_submissions}
          </div>
          <div className="text-xs text-urban-grey/60">Successful</div>
        </div>
        
        <div className="text-center p-3 bg-cloud-white/50 rounded-locale">
          <div className="text-lg font-bold text-muted-coral">
            {status.failed_submissions}
          </div>
          <div className="text-xs text-urban-grey/60">Failed</div>
        </div>
      </div>

      {/* Device List */}
      {devices.length > 0 && (
        <div className="border-t border-grid-lines pt-4">
          <h4 className="text-sm font-medium text-urban-grey mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Active Devices ({devices.length})
          </h4>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {devices.slice(0, 5).map((device) => (
              <div key={device.device_id} className="flex items-center justify-between p-2 bg-cloud-white/30 rounded-locale text-sm">
                <div>
                  <div className="font-medium text-urban-grey">
                    {device.domain}
                  </div>
                  <div className="text-xs text-urban-grey/60 font-mono">
                    {device.device_id.slice(-12)}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-smart-city-teal">
                    {device.total_submissions}
                  </div>
                  <div className={`text-xs ${
                    device.status === 'active' ? 'text-accent-lime' : 'text-urban-grey/60'
                  }`}>
                    {device.status}
                  </div>
                </div>
              </div>
            ))}
            {devices.length > 5 && (
              <div className="text-center text-xs text-urban-grey/60 py-2">
                +{devices.length - 5} more devices
              </div>
            )}
          </div>
        </div>
      )}

      {/* Live Activity Indicator */}
      {status.running && connected && !status.paused && (
        <div className="mt-4 p-3 bg-accent-lime/10 rounded-locale">
          <div className="flex items-center gap-2 text-sm text-accent-lime">
            <div className="w-2 h-2 bg-accent-lime rounded-full animate-pulse"></div>
            <span>Live simulation active</span>
          </div>
        </div>
      )}

      {/* Paused Indicator */}
      {status.paused && (
        <div className="mt-4 p-3 bg-warm-amber/10 rounded-locale">
          <div className="flex items-center gap-2 text-sm text-warm-amber">
            <Pause className="w-4 h-4" />
            <span>Simulation paused</span>
          </div>
        </div>
      )}
    </div>
  );
};
