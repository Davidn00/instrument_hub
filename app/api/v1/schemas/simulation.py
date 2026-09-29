from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


class SineSignalRequest(BaseModel):
    signal_type: Literal["sine"] = "sine"

    frequency: float = Field(
        default=10.0,
        gt=0,
        le=5000,
    )

    amplitude: float = Field(
        default=1.0,
        ge=0,
    )

    sampling_rate: float = Field(
        default=1000.0,
        gt=0,
        le=10000,
    )

    duration: float = Field(
        default=1.0,
        gt=0,
        le=60,
    )

    phase: float = 0.0

    offset: float = 0.0


class NoiseSignalRequest(BaseModel):
    signal_type: Literal["noise"] = "noise"

    amplitude: float = Field(
        default=1.0,
        ge=0,
    )

    sampling_rate: float = Field(
        default=1000.0,
        gt=0,
        le=10000,
    )

    duration: float = Field(
        default=1.0,
        gt=0,
        le=60,
    )

    seed: int | None = None


class ECGSignalRequest(BaseModel):
    signal_type: Literal["ecg"] = "ecg"

    sampling_rate: float = Field(
        default=500.0,
        gt=0,
        le=10000,
    )

    duration: float = Field(
        default=10.0,
        gt=0,
        le=60,
    )

    heart_rate: float = Field(
        default=72.0,
        gt=0,
        le=250,
    )

    amplitude: float = Field(
        default=1.0,
        ge=0,
    )

    noise_amplitude: float = Field(
        default=0.01,
        ge=0,
    )

    seed: int | None = None


class EMGSignalRequest(BaseModel):
    signal_type: Literal["emg"] = "emg"

    sampling_rate: float = Field(
        default=1000.0,
        gt=0,
        le=10000,
    )

    duration: float = Field(
        default=5.0,
        gt=0,
        le=60,
    )

    amplitude: float = Field(
        default=1.0,
        ge=0,
    )

    burst_frequency: float = Field(
        default=50.0,
        gt=0,
        le=5000,
    )

    noise_amplitude: float = Field(
        default=0.05,
        ge=0,
    )

    seed: int | None = None


class FBGSpectrumRequest(BaseModel):
    signal_type: Literal["fbg_spectrum"] = "fbg_spectrum"

    center_wavelength: float = Field(
        default=1550.23,
        gt=0,
    )

    wavelength_start: float = Field(
        default=1548.0,
        gt=0,
    )

    wavelength_end: float = Field(
        default=1552.0,
        gt=0,
    )

    points: int = Field(
        default=2000,
        ge=2,
        le=10000,
    )

    amplitude: float = Field(
        default=1.0,
        ge=0,
    )

    linewidth: float = Field(
        default=0.08,
        gt=0,
    )

    noise_amplitude: float = Field(
        default=0.0,
        ge=0,
    )

    seed: int | None = None


GenerateSignalRequest = Annotated[
    SineSignalRequest
    | NoiseSignalRequest
    | ECGSignalRequest
    | EMGSignalRequest
    | FBGSpectrumRequest,
    Field(discriminator="signal_type"),
]


class GenerateSignalResponse(BaseModel):
    signal_type: str

    samples: list[float]

    sampling_rate: float

    unit: str

    metadata: dict[str, Any] = Field(default_factory=dict)


class DeviceMeasurementRequest(BaseModel):
    device_id: str = Field(
        min_length=1,
        max_length=100,
    )


class DeviceMeasurementResponse(BaseModel):
    timestamp: str

    device_id: str

    channel: str

    value: float

    unit: str

    quality: str

    sensor_id: str

    measurement_type: str

    metadata: dict[str, Any] = Field(default_factory=dict)


class DeviceAcquisitionRequest(BaseModel):
    device_id: str = Field(
        min_length=1,
        max_length=100,
    )

    duration: float = Field(
        default=5.0,
        gt=0,
        le=60,
    )


class DeviceAcquisitionResponse(BaseModel):
    device_id: str

    channel: str

    sampling_rate: float

    unit: str

    number_of_samples: int

    duration: float

    samples: list[float]

    metadata: dict[str, Any] = Field(default_factory=dict)


class SimulatedDeviceInfo(BaseModel):
    device_type: str

    name: str

    description: str
