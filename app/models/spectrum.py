from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import numpy as np


@dataclass(slots=True)
class Spectrum:
    """Optical spectrum acquired from an instrument."""

    timestamp: datetime
    device_id: str
    wavelength: np.ndarray
    intensity: np.ndarray
    wavelength_unit: str = "nm"
    intensity_unit: str = "counts"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=UTC)

        if not self.device_id:
            raise ValueError("device_id cannot be empty")

        if not self.wavelength_unit:
            raise ValueError("wavelength_unit cannot be empty")

        if not self.intensity_unit:
            raise ValueError("intensity_unit cannot be empty")

        self.wavelength = np.asarray(
            self.wavelength,
            dtype=float,
        )

        self.intensity = np.asarray(
            self.intensity,
            dtype=float,
        )

        if self.wavelength.ndim != 1:
            raise ValueError("wavelength must be one-dimensional")

        if self.intensity.ndim != 1:
            raise ValueError("intensity must be one-dimensional")

        if len(self.wavelength) == 0:
            raise ValueError("spectrum cannot be empty")

        if len(self.wavelength) != len(self.intensity):
            raise ValueError("wavelength and intensity must have the same length")

        if not np.all(np.isfinite(self.wavelength)):
            raise ValueError("wavelength contains non-finite values")

        if not np.all(np.isfinite(self.intensity)):
            raise ValueError("intensity contains non-finite values")

    @property
    def number_of_pixels(self) -> int:
        return len(self.intensity)

    @property
    def peak_index(self) -> int:
        return int(np.argmax(self.intensity))

    @property
    def peak_wavelength(self) -> float:
        return float(self.wavelength[self.peak_index])

    @property
    def peak_intensity(self) -> float:
        return float(self.intensity[self.peak_index])
