from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, cast

import numpy as np
from scipy import signal as scipy_signal

from app.models.fbg import (
    FBGPeak,
    FBGPeakDetectionResult,
    FBGTrackingPoint,
    FBGTrackingResult,
)
from app.models.spectrum import Spectrum
from app.processing.statistics import as_float_array, rms


def reduce_spectrum_noise(
    spectrum: Spectrum,
    *,
    window_length: int = 11,
    polyorder: int = 3,
) -> Spectrum:
    """Reduce spectral noise with a Savitzky-Golay filter.

    The wavelength axis is preserved unchanged.
    """

    if window_length <= polyorder:
        raise ValueError("window_length must be greater than polyorder")

    if window_length < 3:
        raise ValueError("window_length must be at least 3")

    if window_length % 2 == 0:
        raise ValueError("window_length must be odd")

    if window_length > spectrum.number_of_pixels:
        raise ValueError("window_length cannot exceed spectrum length")

    filtered = scipy_signal.savgol_filter(
        spectrum.intensity,
        window_length=window_length,
        polyorder=polyorder,
    )

    return Spectrum(
        timestamp=spectrum.timestamp,
        device_id=spectrum.device_id,
        wavelength=spectrum.wavelength.copy(),
        intensity=filtered,
        wavelength_unit=spectrum.wavelength_unit,
        intensity_unit=spectrum.intensity_unit,
        metadata={
            **spectrum.metadata,
            "noise_reduction": "savitzky_golay",
            "savgol_window_length": window_length,
            "savgol_polyorder": polyorder,
        },
    )


def detect_bragg_peaks(
    spectrum: Spectrum,
    *,
    prominence: float | None = None,
    height: float | None = None,
    distance: int | None = None,
    width: float | None = None,
    noise_reduction: bool = True,
    noise_window_length: int = 11,
    noise_polyorder: int = 3,
    refinement: str = "quadratic",
) -> FBGPeakDetectionResult:
    """Detect Bragg peaks using scipy.signal.find_peaks.

    Quadratic refinement uses the three samples around each detected
    discrete maximum to estimate a sub-pixel peak position.
    """

    if distance is not None and distance <= 0:
        raise ValueError("distance must be greater than zero")

    if width is not None and width <= 0:
        raise ValueError("width must be greater than zero")

    if refinement not in {"none", "quadratic"}:
        raise ValueError("refinement must be 'none' or 'quadratic'")

    working = (
        reduce_spectrum_noise(
            spectrum,
            window_length=noise_window_length,
            polyorder=noise_polyorder,
        )
        if noise_reduction
        else spectrum
    )

    indices, properties = scipy_signal.find_peaks(
        working.intensity,
        prominence=prominence,
        height=height,
        distance=distance,
        width=width,
    )
    peak_properties = cast(Mapping[str, Any], properties)

    prominences = (
        np.asarray(peak_properties["prominences"])
        if "prominences" in peak_properties
        else None
    )

    widths = (
        np.asarray(peak_properties["widths"]) if "widths" in peak_properties else None
    )

    peaks: list[FBGPeak] = []

    for position, index_value in enumerate(indices):
        index = int(index_value)

        wavelength = float(working.wavelength[index])

        if refinement == "quadratic":
            wavelength = _quadratic_peak_wavelength(
                working.wavelength,
                working.intensity,
                index,
            )

        prominence_value = (
            float(prominences[position]) if prominences is not None else None
        )

        width_nm = None

        if widths is not None:
            width_nm = _interpolate_width_nm(
                working.wavelength,
                float(widths[position]),
                index,
            )

        peaks.append(
            FBGPeak(
                index=index,
                wavelength_nm=wavelength,
                intensity=float(working.intensity[index]),
                prominence=prominence_value,
                width_nm=width_nm,
            )
        )

    return FBGPeakDetectionResult(
        peaks=tuple(peaks),
        filtered_intensity=working.intensity.copy(),
    )


def detect_bragg_peak(
    spectrum: Spectrum,
    **kwargs: Any,
) -> FBGPeak:
    """Return the strongest detected Bragg peak."""

    result = detect_bragg_peaks(
        spectrum,
        **kwargs,
    )

    if not result.peaks:
        raise ValueError("No Bragg peak was detected")

    return max(
        result.peaks,
        key=lambda peak: (
            peak.prominence if peak.prominence is not None else peak.intensity
        ),
    )


def track_bragg_wavelength(
    spectra: Sequence[Spectrum],
    *,
    reference_wavelength_nm: float | None = None,
    **detection_kwargs: Any,
) -> FBGTrackingResult:
    """Track the selected Bragg wavelength across consecutive spectra."""

    if not spectra:
        raise ValueError("spectra cannot be empty")

    detected = [
        detect_bragg_peak(
            spectrum,
            **detection_kwargs,
        )
        for spectrum in spectra
    ]

    reference = (
        detected[0].wavelength_nm
        if reference_wavelength_nm is None
        else reference_wavelength_nm
    )

    if not np.isfinite(reference) or reference <= 0:
        raise ValueError("reference_wavelength_nm must be finite and greater than zero")

    points = tuple(
        FBGTrackingPoint(
            timestamp=spectrum.timestamp,
            wavelength_nm=peak.wavelength_nm,
            delta_wavelength_nm=peak.wavelength_nm - reference,
            peak_intensity=peak.intensity,
        )
        for spectrum, peak in zip(
            spectra,
            detected,
            strict=True,
        )
    )

    return FBGTrackingResult(
        reference_wavelength_nm=float(reference),
        points=points,
    )


def delta_wavelength(
    wavelength_nm: Sequence[float] | np.ndarray,
    *,
    reference_wavelength_nm: float,
) -> np.ndarray:
    """Calculate Δλ = λ(t) - λ0."""

    values = as_float_array(np.asarray(wavelength_nm, dtype=float))

    if not np.isfinite(reference_wavelength_nm):
        raise ValueError("reference_wavelength_nm must be finite")

    return values - reference_wavelength_nm


@dataclass(frozen=True, slots=True)
class FBGSpectrumMetrics:
    """Scalar metrics commonly exported for LabVIEW comparison."""

    peak_wavelength_nm: float
    peak_amplitude: float
    rms: float


def spectrum_metrics(
    spectrum: Spectrum,
    *,
    noise_reduction: bool = True,
    noise_window_length: int = 11,
    noise_polyorder: int = 3,
) -> FBGSpectrumMetrics:
    """Calculate peak position, peak amplitude and RMS for one spectrum."""

    working = (
        reduce_spectrum_noise(
            spectrum,
            window_length=noise_window_length,
            polyorder=noise_polyorder,
        )
        if noise_reduction
        else spectrum
    )

    peak = detect_bragg_peak(
        working,
        noise_reduction=False,
    )

    return FBGSpectrumMetrics(
        peak_wavelength_nm=peak.wavelength_nm,
        peak_amplitude=peak.intensity,
        rms=rms(working.intensity),
    )


def tracking_frequency(
    tracking: FBGTrackingResult,
) -> float:
    """Estimate the dominant temporal frequency of tracked λB.

    The tracking timestamps must be uniformly sampled enough for an FFT
    interpretation. At least three points are required.
    """

    if len(tracking.points) < 3:
        raise ValueError("at least three tracking points are required")

    timestamps = np.asarray(
        [point.timestamp.timestamp() for point in tracking.points],
        dtype=float,
    )

    values = np.asarray(
        [point.wavelength_nm for point in tracking.points],
        dtype=float,
    )

    intervals = np.diff(timestamps)

    if np.any(intervals <= 0):
        raise ValueError("tracking timestamps must be strictly increasing")

    sampling_interval = float(np.median(intervals))

    if not np.allclose(
        intervals,
        sampling_interval,
        rtol=1e-3,
        atol=1e-9,
    ):
        raise ValueError("tracking timestamps must be approximately uniform")

    centered = values - np.mean(values)

    frequencies = np.fft.rfftfreq(
        values.size,
        d=sampling_interval,
    )

    amplitudes = np.abs(np.fft.rfft(centered))

    if amplitudes.size <= 1:
        return 0.0

    return float(frequencies[1 + int(np.argmax(amplitudes[1:]))])


@dataclass(frozen=True, slots=True)
class ComparisonMetric:
    """Error and correlation metrics for one LabVIEW comparison series."""

    name: str
    absolute_error: float
    relative_error: float
    rmse: float
    correlation: float


@dataclass(frozen=True, slots=True)
class FBGValidationReport:
    """Comparison between InstrumentHub and an external reference."""

    metrics: tuple[ComparisonMetric, ...]

    def by_name(
        self,
        name: str,
    ) -> ComparisonMetric:
        for metric in self.metrics:
            if metric.name == name:
                return metric

        raise KeyError(name)


def compare_series(
    reference: Sequence[float] | np.ndarray,
    candidate: Sequence[float] | np.ndarray,
    *,
    name: str = "series",
) -> ComparisonMetric:
    """Compare two aligned numeric series."""

    expected = as_float_array(np.asarray(reference, dtype=float))
    actual = as_float_array(np.asarray(candidate, dtype=float))

    if expected.size != actual.size:
        raise ValueError("reference and candidate must have the same length")

    error = actual - expected
    absolute = np.abs(error)

    reference_scale = float(np.mean(np.abs(expected)))

    relative = (
        float(np.mean(absolute) / reference_scale)
        if reference_scale > 0
        else (0.0 if np.allclose(actual, expected) else float("inf"))
    )

    correlation = _pearson_correlation(
        expected,
        actual,
    )

    return ComparisonMetric(
        name=name,
        absolute_error=float(np.mean(absolute)),
        relative_error=relative,
        rmse=float(np.sqrt(np.mean(np.square(error)))),
        correlation=correlation,
    )


def validate_against_labview(
    instrumenthub: dict[
        str,
        Sequence[float] | np.ndarray,
    ],
    labview: dict[
        str,
        Sequence[float] | np.ndarray,
    ],
) -> FBGValidationReport:
    """Compare common LabVIEW/InstrumentHub result series.

    Recommended keys are:
        wavelength_nm
        delta_wavelength_nm
        peak_position_nm
        amplitude
        rms
        frequency_hz
        temporal_results

    Missing keys are skipped so a validation run can use the quantities
    actually available from the LabVIEW export.
    """

    metrics: list[ComparisonMetric] = []

    for name in (
        "wavelength_nm",
        "delta_wavelength_nm",
        "peak_position_nm",
        "amplitude",
        "rms",
        "frequency_hz",
        "temporal_results",
    ):
        if name in instrumenthub and name in labview:
            metrics.append(
                compare_series(
                    labview[name],
                    instrumenthub[name],
                    name=name,
                )
            )

    if not metrics:
        raise ValueError("No common validation series were provided")

    return FBGValidationReport(metrics=tuple(metrics))


def _quadratic_peak_wavelength(
    wavelength: np.ndarray,
    intensity: np.ndarray,
    index: int,
) -> float:
    if index == 0 or index == intensity.size - 1:
        return float(wavelength[index])

    y_left = float(intensity[index - 1])

    y_center = float(intensity[index])

    y_right = float(intensity[index + 1])

    denominator = y_left - 2.0 * y_center + y_right

    if denominator == 0.0:
        return float(wavelength[index])

    offset = 0.5 * (y_left - y_right) / denominator

    offset = float(
        np.clip(
            offset,
            -1.0,
            1.0,
        )
    )

    spacing_left = float(wavelength[index] - wavelength[index - 1])

    spacing_right = float(wavelength[index + 1] - wavelength[index])

    spacing = (spacing_left + spacing_right) / 2.0

    return float(wavelength[index] + offset * spacing)


def _interpolate_width_nm(
    wavelength: np.ndarray,
    width_points: float,
    index: int,
) -> float:
    if wavelength.size < 2:
        return 0.0

    if index == 0:
        spacing = wavelength[1] - wavelength[0]
    elif index == wavelength.size - 1:
        spacing = wavelength[-1] - wavelength[-2]
    else:
        spacing = (wavelength[index + 1] - wavelength[index - 1]) / 2.0

    return float(abs(width_points * spacing))


def _pearson_correlation(
    reference: np.ndarray,
    candidate: np.ndarray,
) -> float:
    if reference.size < 2:
        return float("nan")

    reference_std = float(np.std(reference))

    candidate_std = float(np.std(candidate))

    if reference_std == 0.0 or candidate_std == 0.0:
        return float("nan")

    return float(
        np.corrcoef(
            reference,
            candidate,
        )[0, 1]
    )
