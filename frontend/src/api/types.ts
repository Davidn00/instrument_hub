
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

export interface SpectrumStreamEvent {
  type: "spectrum";
  data?: Spectrum;
  payload?: Spectrum;
  spectrum?: Spectrum;
}

export interface MeasurementStreamEvent {
  type: "measurement";
  data?: Measurement;
  payload?: Measurement;
}

export type AcquisitionStreamEvent =
  | SpectrumStreamEvent
  | MeasurementStreamEvent;

export type WebSocketConnectionStatus =
  | "connecting"
  | "connected"
  | "reconnecting"
  | "disconnected"
  | "error";


export interface MeasurementSeries {
  key: string;
  label: string;
  deviceId: string;
  channel: string;
  unit: string;
  points: Measurement[];
}

export interface FftAnalysisRequest {
  samples: number[];
  sampling_rate_hz: number;
  remove_mean: boolean;
}

export interface FftAnalysisResponse {
  sample_count: number;
  sampling_rate_hz: number;
  time_seconds: number[];
  signal_values: number[];
  frequencies_hz: number[];
  amplitudes: number[];
  dominant_frequency_hz: number;
  remove_mean: boolean;
}


export interface FBGPeakResult {
  index: number;
  wavelength_nm: number;
  intensity: number;
  prominence: number | null;
  width_nm: number | null;
}

export interface FBGTrackingPoint {
  timestamp: string;
  wavelength_nm: number;
  delta_wavelength_nm: number;
  peak_intensity: number;
}

export interface FBGAnalysisRequest {
  device_id: string;
  spectrum_timestamp?: string | null;
  history_limit?: number;
  prominence?: number | null;
  height?: number | null;
  distance?: number | null;
  width?: number | null;
  noise_reduction?: boolean;
  noise_window_length?: number;
  noise_polyorder?: number;
  refinement?: "none" | "quadratic";
  reference_wavelength_nm?: number | null;
}

export interface FBGAnalysisResponse {
  device_id: string;
  spectrum: Spectrum;
  filtered_intensity: number[];
  peaks: FBGPeakResult[];
  peak_wavelength_nm: number | null;
  peak_intensity: number | null;
  rms: number;
  reference_wavelength_nm: number | null;
  tracking_points: FBGTrackingPoint[];
  analyzed_spectra_count: number;
  noise_reduction: boolean;
  noise_window_length: number;
  noise_polyorder: number;
  prominence: number | null;
  refinement: "none" | "quadratic";
}
