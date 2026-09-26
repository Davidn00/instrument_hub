# InstrumentHub — Stage 2
# Instrument Simulation

## Objective

Stage 2 introduces a complete software simulation layer for
instrumentation data.

The objective is to allow development and testing without requiring
physical instrumentation hardware.

## Architecture

```text
                    InstrumentHub
                         |
                         v
                InstrumentDevice
                         |
              +----------+----------+
              |                     |
              v                     v
      SimulatedDevice          Future Hardware
              |
      +-------+-------+
      |       |       |
      v       v       v
 Temperature Pressure Waveforms
                         |
              +----------+----------+
              |          |          |
              v          v          v
             ECG        EMG         FBG
                         |
                         v
                  Signal / Measurement
                         |
                         v
                  Acquisition Layer

Device abstraction

All devices implement the common instrument interface.

The main operations are:

connect
disconnect
read

Simulation devices extend the common SimulatedDevice abstraction.

This allows future hardware drivers to replace simulated devices
without modifying the higher-level application architecture.

Supported simulated devices
Temperature

Produces temperature measurements in degrees Celsius.

Pressure

Produces pressure measurements in kPa.

Sine waveform

Produces configurable sinusoidal signals.

ECG

Produces synthetic ECG-like signals.

The ECG implementation is intended exclusively for software simulation
and testing. It is not a clinical or diagnostic model.

EMG

Produces synthetic EMG-like signals.

The EMG implementation is intended exclusively for software simulation
and testing.

FBG

Produces synthetic Fiber Bragg Grating spectra.

The simulated spectrum includes:

center wavelength
wavelength range
linewidth
amplitude
optional noise
Signal generators

The following generators are available:

generate_sine()
generate_noise()
generate_ecg()
generate_emg()
generate_fbg_spectrum()

All generators are deterministic when a random seed is provided.

Dataset support

InstrumentHub supports:

CSV
JSON
Parquet

Datasets are loaded through DatasetLoader.

Dataset normalization is performed before playback when necessary.

Dataset playback

DatasetPlayer supports:

immediate playback
real-time playback
configurable playback speed
timestamp-based delays

Testing

Stage 2 tests cover:

signal length
signal amplitude
deterministic random generation
ECG generation
EMG generation
FBG spectrum generation
simulator lifecycle
dataset loading
dataset normalization
CSV support
JSON support
Parquet support
playback
real-time playback
playback speed
API endpoints
integration between simulation services and domain models
