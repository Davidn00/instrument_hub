import math

from pydantic import BaseModel, Field, field_validator


class FftAnalysisRequest(BaseModel):
    """Request payload for real-valued FFT analysis."""

    samples: list[float] = Field(
        min_length=16,
        max_length=4096,
    )
    sampling_rate_hz: float = Field(
        gt=0,
        le=1_000_000,
    )
    remove_mean: bool = True

    @field_validator("samples")
    @classmethod
    def validate_finite_samples(
        cls,
        values: list[float],
    ) -> list[float]:
        if not all(math.isfinite(value) for value in values):
            raise ValueError("All samples must be finite numbers.")

        return values


class FftAnalysisResponse(BaseModel):
    """FFT results returned to the dashboard."""

    sample_count: int
    sampling_rate_hz: float
    time_seconds: list[float]
    signal_values: list[float]
    frequencies_hz: list[float]
    amplitudes: list[float]
    dominant_frequency_hz: float
    remove_mean: bool
