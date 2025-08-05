import { toast } from 'react-hot-toast';

export interface InputRecord {
  index: number;
  block_number: number;
  timestamp: string;
  msg_sender: string;
  payload: any;
  status: string;
}

export interface DecryptedPayload {
  device_id: string;
  timestamp: number;
  domain: string;
  sensor_type: string;
  temperature?: number;
  humidity?: number;
  air_quality_index?: number;
  transaction_value?: number;
  signal_strength_dbm?: number;
  privacy_metadata: {
    pii_removed: boolean;
    location_anonymized: boolean;
    encryption_ready: boolean;
    privacy_score: number;
  };
}

export interface AggregatedData {
  domain: string;
  device_count: number;
  total_readings: number;
  avg_temperature?: number;
  avg_humidity?: number;
  avg_transaction_value?: number;
  avg_signal_strength?: number;
  privacy_score: number;
}

const API_BASE_URL = process.env.VITE_DATA_EXPLORER_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://data-explorer-api-production.up.railway.app' 
    : 'http://localhost:8091');

export class DataExplorerService {
  private static instance: DataExplorerService;

  static getInstance(): DataExplorerService {
    if (!DataExplorerService.instance) {
      DataExplorerService.instance = new DataExplorerService();
    }
    return DataExplorerService.instance;
  }

  async fetchInputRecords(deviceType?: string, limit: number = 50): Promise<InputRecord[]> {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        ...(deviceType && deviceType !== 'all' && { device_type: deviceType }),
        block_number_min: '108500' // Only fetch recent inputs
      });

      const response = await fetch(`${API_BASE_URL}/api/inputs?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.records;
    } catch (error) {
      console.error('Failed to fetch input records:', error);
      toast.error('Failed to load input records');
      throw error;
    }
  }

  async decryptInputData(records: InputRecord[]): Promise<DecryptedPayload[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/decrypt-batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          records: records
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.decrypted_data;
    } catch (error) {
      console.error('Failed to decrypt data:', error);
      toast.error('Failed to decrypt sensor data');
      throw error;
    }
  }

  async generateAggregatedReport(decryptedData: DecryptedPayload[]): Promise<AggregatedData[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(decryptedData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.analytics;
    } catch (error) {
      console.error('Failed to generate aggregated report:', error);
      toast.error('Failed to generate analytics');
      throw error;
    }
  }

  async callDecryptionScript(inputIndex: number, deviceId: string): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/decrypt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          index: inputIndex,
          device_id: deviceId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to decrypt via script:', error);
      throw error;
    }
  }
}

export const dataExplorerService = DataExplorerService.getInstance();