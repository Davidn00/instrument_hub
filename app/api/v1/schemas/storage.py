from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ChannelCreate(BaseModel):
    name: str
    unit: str
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DeviceCreate(BaseModel):
    device_id: str
    name: str
    device_type: str
    interface: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    channels: list[ChannelCreate] = Field(default_factory=list)


class DeviceResponse(BaseModel):
    id: UUID
    device_id: str
    name: str
    device_type: str
    interface: str | None
    status: str
    metadata: dict[str, Any]


class MeasurementResponse(BaseModel):
    timestamp: datetime
    device_id: str
    channel: str
    value: float
    unit: str
    quality: str
    metadata: dict[str, Any]


class SpectrumResponse(BaseModel):
    id: UUID | None = None
    timestamp: datetime
    device_id: str
    wavelength: list[float]
    intensity: list[float]
    wavelength_unit: str
    intensity_unit: str
    metadata: dict[str, Any]


class SpectrumCreate(BaseModel):
    timestamp: datetime
    device_id: str
    wavelength: list[float]
    intensity: list[float]
    wavelength_unit: str = "nm"
    intensity_unit: str = "counts"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentConfiguration(BaseModel):
    """Parámetros reproducibles de un experimento."""

    # Identificadores de dispositivos registrados en InstrumentHub.
    device_ids: list[str] = Field(default_factory=list)

    # Nombres de canales que se desean registrar.
    sensors: list[str] = Field(default_factory=list)

    # Parámetros de adquisición; por ejemplo, sampling_rate_hz.
    acquisition: dict[str, Any] = Field(default_factory=dict)

    # Parámetros de procesamiento; por ejemplo, filtros y FFT.
    processing: dict[str, Any] = Field(default_factory=dict)


class ExperimentCreate(BaseModel):
    """Datos de entrada para crear un experimento."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    configuration: ExperimentConfiguration = Field(
        default_factory=ExperimentConfiguration
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        # Evita guardar nombres vacíos o compuestos únicamente por espacios.
        value = value.strip()
        if not value:
            raise ValueError("Experiment name cannot be empty.")
        return value


class ExperimentStatusUpdate(BaseModel):
    """Transiciones explícitas del ciclo de vida."""

    status: Literal["RUNNING", "COMPLETED", "FAILED", "CANCELLED"]


class ExperimentResultCreate(BaseModel):
    """Resultado de procesamiento asociado al experimento."""

    result_type: str = Field(min_length=1, max_length=100)
    data: dict[str, Any] = Field(default_factory=dict)
    summary: str | None = None


class ExperimentResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    status: str
    started_at: datetime | None
    ended_at: datetime | None
    metadata: dict[str, Any]


class AcquisitionRequest(BaseModel):
    device_id: str
