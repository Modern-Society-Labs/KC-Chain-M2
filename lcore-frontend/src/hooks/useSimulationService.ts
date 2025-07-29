import { useState, useEffect, useCallback } from 'react';

interface SimulationStatus {
  running: boolean;
  paused: boolean;
  devices_active: number;
  total_submissions: number;
  successful_submissions: number;
  failed_submissions: number;
  uptime_seconds: number;
  last_submission?: string;
}

interface DeviceInfo {
  device_id: string;
  domain: string;
  did_format: string;
  status: string;
  total_submissions: number;
  last_submission?: string;
  submission_interval: number;
}

interface SimulationUpdate {
  timestamp: string;
  event_type: string;
  device_id?: string;
  data: Record<string, any>;
}

const SIMULATION_API_BASE = 'http://localhost:8080';

export const useSimulationService = () => {
  const [status, setStatus] = useState<SimulationStatus>({
    running: false,
    paused: false,
    devices_active: 0,
    total_submissions: 0,
    successful_submissions: 0,
    failed_submissions: 0,
    uptime_seconds: 0
  });
  
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [connected, setConnected] = useState(false);
  const [interval, setInterval] = useState(35.0);  // Updated to match new 3-day default
  const [lastUpdate, setLastUpdate] = useState<SimulationUpdate | null>(null);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8080/ws`);
    
    ws.onopen = () => {
      setConnected(true);
      console.log('Connected to simulation service');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'initial_state') {
          setStatus(data.status);
          setDevices(data.devices);
          setInterval(data.config.interval);
        } else {
          // Handle real-time updates
          const update: SimulationUpdate = data;
          setLastUpdate(update);
          
          if (update.event_type === 'status_change') {
            setStatus(update.data as SimulationStatus);
          } else if (update.event_type === 'device_submission') {
            // Update device info
            setDevices(prev => prev.map(device => 
              device.device_id === update.device_id 
                ? { ...device, total_submissions: update.data.submission_count }
                : device
            ));
          } else if (update.event_type === 'config_change') {
            setInterval(update.data.new_interval);
          }
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    ws.onclose = () => {
      setConnected(false);
      console.log('Disconnected from simulation service');
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };
    
    return () => {
      ws.close();
    };
  }, []);

  const startSimulation = useCallback(async () => {
    try {
      const response = await fetch(`${SIMULATION_API_BASE}/simulation/start`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to start simulation');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error starting simulation:', error);
      throw error;
    }
  }, []);

  const stopSimulation = useCallback(async () => {
    try {
      const response = await fetch(`${SIMULATION_API_BASE}/simulation/stop`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to stop simulation');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error stopping simulation:', error);
      throw error;
    }
  }, []);

  const pauseSimulation = useCallback(async () => {
    try {
      const response = await fetch(`${SIMULATION_API_BASE}/simulation/pause`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to pause simulation');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error pausing simulation:', error);
      throw error;
    }
  }, []);

  const resumeSimulation = useCallback(async () => {
    try {
      const response = await fetch(`${SIMULATION_API_BASE}/simulation/resume`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to resume simulation');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error resuming simulation:', error);
      throw error;
    }
  }, []);

  const restartSimulation = useCallback(async () => {
    try {
      const response = await fetch(`${SIMULATION_API_BASE}/simulation/restart`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to restart simulation');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error restarting simulation:', error);
      throw error;
    }
  }, []);

  const updateInterval = useCallback(async (newInterval: number) => {
    try {
      const response = await fetch(`${SIMULATION_API_BASE}/simulation/interval`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ interval: newInterval }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update interval');
      }
      
      setInterval(newInterval);
      return await response.json();
    } catch (error) {
      console.error('Error updating interval:', error);
      throw error;
    }
  }, []);

  const getHealthStatus = useCallback(async () => {
    try {
      const response = await fetch(`${SIMULATION_API_BASE}/health`);
      return await response.json();
    } catch (error) {
      console.error('Error getting health status:', error);
      return null;
    }
  }, []);

  return {
    status,
    devices,
    connected,
    interval,
    lastUpdate,
    startSimulation,
    stopSimulation,
    pauseSimulation,
    resumeSimulation,
    restartSimulation,
    updateInterval,
    getHealthStatus
  };
};
