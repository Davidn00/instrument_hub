from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


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


class ExperimentCreate(BaseModel):
    name: str
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


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
