from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.api.v1.schemas.storage import SpectrumResponse


class FBGAnalysisRequest(BaseModel):
    device_id: str = Field(min_length=1)
    spectrum_timestamp: datetime | None = None
    history_limit: int = Field(default=100, ge=1, le=1000)

    prominence: float | None = Field(default=None, ge=0)
    height: float | None = None
    distance: int | None = Field(default=None, ge=1)
    width: float | None = Field(default=None, gt=0)

    noise_reduction: bool = True
    noise_window_length: int = Field(default=11, ge=3, le=101)
    noise_polyorder: int = Field(default=3, ge=1, le=5)
    refinement: Literal["none", "quadratic"] = "quadratic"

    reference_wavelength_nm: float | None = Field(default=None, gt=0)


class FBGPeakResponse(BaseModel):
    index: int
    wavelength_nm: float
    intensity: float
    prominence: float | None
    width_nm: float | None


class FBGTrackingPointResponse(BaseModel):
    timestamp: datetime
    wavelength_nm: float
    delta_wavelength_nm: float
    peak_intensity: float


class FBGAnalysisResponse(BaseModel):
    device_id: str
    spectrum: SpectrumResponse
    filtered_intensity: list[float]
    peaks: list[FBGPeakResponse]

    peak_wavelength_nm: float | None
    peak_intensity: float | None
    rms: float

    reference_wavelength_nm: float | None
    tracking_points: list[FBGTrackingPointResponse]
    analyzed_spectra_count: int

    noise_reduction: bool
    noise_window_length: int
    noise_polyorder: int
    prominence: float | None
    refinement: Literal["none", "quadratic"]
