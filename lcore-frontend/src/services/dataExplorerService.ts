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

const SUPABASE_URL = 'postgresql://postgres.kebutcghyvuutioewxnd:youthinkthereforeiam@aws-0-us-east-1.pooler.supabase.com:5432/postgres';

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
      // For demo, return mock data
      // In production, this would call your backend API that queries Supabase
      const mockRecords: InputRecord[] = [
        {
          index: 23978,
          block_number: 108579,
          timestamp: '2025-08-04T17:59:48',
          msg_sender: '0x879538e0c76a727361',
          payload: {
            type: 'submit_sensor_data',
            device_id: 'did:lcore:env-102-air',
            encrypted_payload: 'eyJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDpsY29yZTplbnYtMTAyLWFpciIsInR5cCI6IkpXVCJ9...'
          },
          status: 'Unprocessed'
        },
        {
          index: 23977,
          block_number: 108578,
          timestamp: '2025-08-04T17:59:47',
          msg_sender: '0x5ee337af165b4c76a',
          payload: {
            type: 'submit_sensor_data',
            device_id: 'did:lcore:health-tracker-3',
            encrypted_payload: 'eyJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDpsY29yZTpoZWFsdGgtdHJhY2tlci0zIiwidHlwIjoiSldUIn0...'
          },
          status: 'Unprocessed'
        },
        {
          index: 23976,
          block_number: 108577,
          timestamp: '2025-08-04T17:59:46',
          msg_sender: '0x8ad29b3f9c09f73a',
          payload: {
            type: 'submit_sensor_data',
            device_id: 'did:lcore:retail-midtown-store-3',
            encrypted_payload: 'eyJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDpsY29yZTpyZXRhaWwtbWlkdG93bi1zdG9yZS0zIiwidHlwIjoiSldUIn0...'
          },
          status: 'Unprocessed'
        }
      ];

      // Filter by device type if specified
      let filteredRecords = mockRecords;
      if (deviceType && deviceType !== 'all') {
        filteredRecords = mockRecords.filter(record => 
          record.payload.device_id.includes(deviceType)
        );
      }

      return filteredRecords.slice(0, limit);
    } catch (error) {
      console.error('Failed to fetch input records:', error);
      toast.error('Failed to load input records');
      throw error;
    }
  }

  async decryptInputData(records: InputRecord[]): Promise<DecryptedPayload[]> {
    try {
      // For demo, return mock decrypted data
      // In production, this would call your Python decryption service
      const mockDecrypted: DecryptedPayload[] = [
        {
          device_id: 'did:lcore:env-102-air',
          timestamp: 1754330387,
          domain: 'environmental',
          sensor_type: 'environmental',
          temperature: 20.0,
          humidity: null,
          air_quality_index: 100,
          privacy_metadata: {
            pii_removed: true,
            location_anonymized: true,
            encryption_ready: true,
            privacy_score: 100
          }
        },
        {
          device_id: 'did:lcore:health-tracker-3',
          timestamp: 1754330385,
          domain: 'health',
          sensor_type: 'health',
          temperature: 36.8,
          privacy_metadata: {
            pii_removed: true,
            location_anonymized: true,
            encryption_ready: true,
            privacy_score: 100
          }
        },
        {
          device_id: 'did:lcore:retail-midtown-store-3',
          timestamp: 1754330383,
          domain: 'retail',
          sensor_type: 'retail',
          transaction_value: 47.99,
          privacy_metadata: {
            pii_removed: true,
            location_anonymized: true,
            encryption_ready: true,
            privacy_score: 100
          }
        }
      ];

      return mockDecrypted;
    } catch (error) {
      console.error('Failed to decrypt data:', error);
      toast.error('Failed to decrypt sensor data');
      throw error;
    }
  }

  async generateAggregatedReport(decryptedData: DecryptedPayload[]): Promise<AggregatedData[]> {
    try {
      // Group data by domain and calculate aggregates
      const domainGroups = decryptedData.reduce((acc, item) => {
        if (!acc[item.domain]) {
          acc[item.domain] = [];
        }
        acc[item.domain].push(item);
        return acc;
      }, {} as Record<string, DecryptedPayload[]>);

      const aggregated: AggregatedData[] = Object.entries(domainGroups).map(([domain, items]) => {
        const temperatures = items.filter(i => i.temperature).map(i => i.temperature!);
        const humidities = items.filter(i => i.humidity).map(i => i.humidity!);
        const transactions = items.filter(i => i.transaction_value).map(i => i.transaction_value!);
        const signals = items.filter(i => i.signal_strength_dbm).map(i => i.signal_strength_dbm!);

        return {
          domain,
          device_count: new Set(items.map(i => i.device_id)).size,
          total_readings: items.length,
          avg_temperature: temperatures.length > 0 
            ? Math.round((temperatures.reduce((a, b) => a + b, 0) / temperatures.length) * 10) / 10
            : undefined,
          avg_humidity: humidities.length > 0
            ? Math.round((humidities.reduce((a, b) => a + b, 0) / humidities.length) * 10) / 10
            : undefined,
          avg_transaction_value: transactions.length > 0
            ? Math.round((transactions.reduce((a, b) => a + b, 0) / transactions.length) * 100) / 100
            : undefined,
          avg_signal_strength: signals.length > 0
            ? Math.round((signals.reduce((a, b) => a + b, 0) / signals.length) * 10) / 10
            : undefined,
          privacy_score: 100 // All data is privacy-compliant
        };
      });

      return aggregated;
    } catch (error) {
      console.error('Failed to generate aggregated report:', error);
      toast.error('Failed to generate analytics');
      throw error;
    }
  }

  async callDecryptionScript(inputIndex: number, deviceId: string): Promise<any> {
    try {
      // This would call your backend endpoint that runs the Python script
      // For demo purposes, return mock data
      const response = await fetch('/api/decrypt', {
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