
export type JsonPrimitive = string | number | boolean | null;

export type JsonValue =
  | JsonPrimitive
  | JsonValue[]
  | { [key: string]: JsonValue };

export type JsonObject = Record<string, JsonValue>;

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
}

export interface ReadinessResponse {
  status: string;
  database: string;
  timescaledb: string;
}

export interface Device {
  id: string;
  device_id: string;
  name: string;
  device_type: string;
  interface: string | null;
  status: string;
  metadata: JsonObject;
}

export interface Measurement {
  timestamp: string;
  device_id: string;
  channel: string;
  value: number;
  unit: string;
  quality: string;
  metadata: JsonObject;
}

export interface Spectrum {
  id: string | null;
  timestamp: string;
  device_id: string;
  wavelength: number[];
  intensity: number[];
  wavelength_unit: string;
  intensity_unit: string;
  metadata: JsonObject;
}

export interface Experiment {
  id: string;
  name: string;
  description: string | null;
  status: string;
  started_at: string | null;
  ended_at: string | null;
  metadata: JsonObject;
}

export interface SimulatedDeviceInfo {
  [key: string]: JsonValue;
}


export interface ChannelCreate {
  name: string;
  unit: string;
  description?: string | null;
  metadata: JsonObject;
}

export interface DeviceCreate {
  device_id: string;
  name: string;
  device_type: string;
  interface?: string | null;
  metadata: JsonObject;
  channels: ChannelCreate[];
}

export interface ExperimentCreate {
  name: string;
  description?: string | null;
  metadata: JsonObject;
}
