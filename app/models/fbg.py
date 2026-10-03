from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import numpy as np


@dataclass(frozen=True, slots=True)
class FBGPeak:
    """Detected and optionally sub-pixel-refined Bragg peak."""

    index: int
    wavelength_nm: float
    intensity: float
    prominence: float | None = None
    width_nm: float | None = None


@dataclass(frozen=True, slots=True)
class FBGPeakDetectionResult:
    """Result of Bragg peak detection on one optical spectrum."""

    peaks: tuple[FBGPeak, ...]
    filtered_intensity: np.ndarray


@dataclass(frozen=True, slots=True)
class FBGTrackingPoint:
    """One temporal Bragg-wavelength tracking sample."""

    timestamp: datetime
    wavelength_nm: float
    delta_wavelength_nm: float
    peak_intensity: float


@dataclass(frozen=True, slots=True)
class FBGTrackingResult:
    """Temporal tracking of a Bragg wavelength."""

    reference_wavelength_nm: float
    points: tuple[FBGTrackingPoint, ...]


@dataclass(frozen=True, slots=True)
class FBGCalibration:
    """Physical FBG calibration model.

    The first-order wavelength shift model is:

        Δλ / λ0 = (1 - pe) * ε + (αf + ξ) * ΔT

    where:
        λ0 = reference Bragg wavelength [nm]
        pe = effective photoelastic constant [-]
        ε  = strain [dimensionless]
        αf = fiber thermal expansion coefficient [1/°C]
        ξ  = thermo-optic coefficient [1/°C]
        ΔT = temperature change [°C]

    Coefficients must come from the sensor/fiber calibration.
    """

    photoelastic_constant: float
    thermal_expansion_coefficient_per_c: float
    thermo_optic_coefficient_per_c: float

    def __post_init__(self) -> None:
        if not np.isfinite(self.photoelastic_constant):
            raise ValueError("photoelastic_constant must be finite")

        if self.photoelastic_constant == 1.0:
            raise ValueError("photoelastic_constant cannot be exactly 1")

        if not np.isfinite(self.thermal_expansion_coefficient_per_c):
            raise ValueError("thermal_expansion_coefficient_per_c must be finite")

        if not np.isfinite(self.thermo_optic_coefficient_per_c):
            raise ValueError("thermo_optic_coefficient_per_c must be finite")

        if (
            self.thermal_expansion_coefficient_per_c
            + self.thermo_optic_coefficient_per_c
            == 0.0
        ):
            raise ValueError("thermal and thermo-optic coefficients cannot sum to zero")

    @property
    def strain_sensitivity(self) -> float:
        """Dimensionless wavelength-shift sensitivity to strain."""

        return 1.0 - self.photoelastic_constant

    @property
    def temperature_sensitivity_per_c(self) -> float:
        """Dimensionless wavelength-shift sensitivity to temperature."""

        return (
            self.thermal_expansion_coefficient_per_c
            + self.thermo_optic_coefficient_per_c
        )

    def strain_from_shift(
        self,
        delta_wavelength_nm: float,
        reference_wavelength_nm: float,
        *,
        delta_temperature_c: float = 0.0,
    ) -> float:
        """Calculate strain from wavelength shift.

        Returns strain as a dimensionless quantity. Multiply by 1e6
        to express it in microstrain (µε).
        """

        _validate_reference_wavelength(reference_wavelength_nm)

        normalized_shift = delta_wavelength_nm / reference_wavelength_nm

        return (
            normalized_shift - self.temperature_sensitivity_per_c * delta_temperature_c
        ) / self.strain_sensitivity

    def microstrain_from_shift(
        self,
        delta_wavelength_nm: float,
        reference_wavelength_nm: float,
        *,
        delta_temperature_c: float = 0.0,
    ) -> float:
        """Calculate strain in microstrain (µε)."""

        return (
            self.strain_from_shift(
                delta_wavelength_nm,
                reference_wavelength_nm,
                delta_temperature_c=delta_temperature_c,
            )
            * 1e6
        )

    def temperature_from_shift(
        self,
        delta_wavelength_nm: float,
        reference_wavelength_nm: float,
        *,
        strain: float = 0.0,
    ) -> float:
        """Calculate temperature change from wavelength shift [°C]."""

        _validate_reference_wavelength(reference_wavelength_nm)

        normalized_shift = delta_wavelength_nm / reference_wavelength_nm

        return (
            normalized_shift - self.strain_sensitivity * strain
        ) / self.temperature_sensitivity_per_c


def _validate_reference_wavelength(value: float) -> None:
    if not np.isfinite(value) or value <= 0:
        raise ValueError("reference_wavelength_nm must be finite and greater than zero")
