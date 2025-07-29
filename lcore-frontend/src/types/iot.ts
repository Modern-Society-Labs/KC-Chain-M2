// L{CORE} IoT Data Types - Community-focused, privacy-preserving

export interface IoTReading {
  device_id: string;
  timestamp: number;
  sensor_type: 'weather' | 'traffic' | 'energy' | 'water' | 'air_quality' | 'network' | 'retail' | 'agricultural' | 'health' | 'environmental';
  reading: number;
  unit: string;
  metadata?: Record<string, any>;
}

export interface Device {
  id: string;
  owner: string;
  device_type: string;
  status: 'online' | 'offline' | 'warning' | 'error';
  last_reading: number;
  created_at: number;
  total_readings: number;
}

export interface SensorType {
  type: string;
  name: string;
  description: string;
  unit: string;
  icon: string;
  color: string;
}

export interface DeviceStats {
  total_devices: number;
  active_devices: number;
  offline_devices: number;
  total_readings_today: number;
  avg_reading_interval: number;
}

export interface DataMarketplaceEntry {
  device_id: string;
  device_type: string;
  price_per_reading: number;
  total_earnings: number;
  access_tier: 'free' | 'community' | 'premium';
  data_quality_score: number;
}

export interface GraphQLInput {
  index: number;
  timestamp: string;
  msgSender: string;
  payload: string;
}

export interface GraphQLNotice {
  index: number;
  input: {
    index: number;
  };
  payload: string;
}

export interface GraphQLVoucher {
  index: number;
  input: {
    index: number;
  };
  destination: string;
  payload: string;
}

export interface GraphQLReport {
  index: number;
  input: {
    index: number;
  };
  payload: string;
}

// Device simulation types
export interface SimulatedDevice {
  id: string;
  name: string;
  type: string;
  status: 'running' | 'stopped';
  interval: number; // seconds
  lastReading?: IoTReading;
}

// Privacy and security types
export interface EncryptionStatus {
  is_encrypted: boolean;
  encryption_method: 'AES-256-GCM' | 'XChaCha20-Poly1305';
  key_derivation: 'SHA-256';
  zk_proof_available: boolean;
}

// Community data aggregation
export interface CommunityMetrics {
  total_community_devices: number;
  readings_per_hour: number;
  average_data_quality: number;
  privacy_compliance_score: number;
  total_community_earnings: number;
}

// Real-time data flow
export interface DataFlowEvent {
  id: string;
  type: 'input' | 'processing' | 'output' | 'voucher';
  timestamp: number;
  payload_preview: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  processing_time?: number;
} 