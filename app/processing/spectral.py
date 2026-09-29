from dataclasses import dataclass

import numpy as np
from scipy import signal as scipy_signal

from app.processing.statistics import as_float_array


@dataclass(frozen=True, slots=True)
class FFTResult:
    """Single-sided real FFT representation."""

    frequencies: np.ndarray
    amplitudes: np.ndarray


@dataclass(frozen=True, slots=True)
class PSDResult:
    """Power spectral density estimated with Welch's method."""

    frequencies: np.ndarray
    power: np.ndarray


def fft_spectrum(
    samples: np.ndarray | list[float] | tuple[float, ...],
    sampling_rate: float,
) -> FFTResult:
    """
    Calculate a single-sided amplitude spectrum for a real signal.
    """

    array = as_float_array(samples)

    if sampling_rate <= 0:
        raise ValueError("sampling_rate must be greater than zero")

    n = array.size

    frequencies = np.fft.rfftfreq(
        n,
        d=1.0 / sampling_rate,
    )

    amplitudes = np.abs(np.fft.rfft(array)) * (2.0 / n)

    # DC and Nyquist bins must not be doubled.
    amplitudes[0] /= 2.0

    if n % 2 == 0 and amplitudes.size > 1:
        amplitudes[-1] /= 2.0

    return FFTResult(
        frequencies=frequencies,
        amplitudes=amplitudes,
    )


def dominant_frequency(
    samples: np.ndarray | list[float] | tuple[float, ...],
    sampling_rate: float,
    *,
    include_dc: bool = False,
) -> float:
    """
    Return the frequency with the greatest amplitude.
    """

    spectrum = fft_spectrum(
        samples,
        sampling_rate,
    )

    start = 0 if include_dc else 1

    if spectrum.amplitudes.size <= start:
        return 0.0

    index = start + int(np.argmax(spectrum.amplitudes[start:]))

    return float(spectrum.frequencies[index])


def power_spectral_density(
    samples: np.ndarray | list[float] | tuple[float, ...],
    sampling_rate: float,
    *,
    nperseg: int | None = None,
) -> PSDResult:
    """
    Estimate PSD using Welch's method.
    """

    array = as_float_array(samples)

    if sampling_rate <= 0:
        raise ValueError("sampling_rate must be greater than zero")

    if nperseg is not None and nperseg <= 0:
        raise ValueError("nperseg must be greater than zero")

    frequencies, power = scipy_signal.welch(
        array,
        fs=sampling_rate,
        nperseg=nperseg,
    )

    return PSDResult(
        frequencies=frequencies,
        power=power,
    )


def detect_harmonics(
    samples: np.ndarray | list[float] | tuple[float, ...],
    sampling_rate: float,
    *,
    fundamental_frequency: float | None = None,
    max_harmonic: int = 5,
    tolerance_hz: float | None = None,
    threshold_ratio: float = 0.05,
) -> list[float]:
    """
    Detect harmonic peaks near integer multiples of a fundamental.
    """

    if max_harmonic < 1:
        raise ValueError("max_harmonic must be greater than zero")

    if threshold_ratio < 0:
        raise ValueError("threshold_ratio cannot be negative")

    spectrum = fft_spectrum(
        samples,
        sampling_rate,
    )

    if fundamental_frequency is None:
        fundamental_frequency = dominant_frequency(
            samples,
            sampling_rate,
        )

    if fundamental_frequency <= 0:
        return []

    if tolerance_hz is None:
        resolution = sampling_rate / len(as_float_array(samples))

        tolerance_hz = max(
            resolution,
            fundamental_frequency * 0.02,
        )

    if tolerance_hz <= 0:
        raise ValueError("tolerance_hz must be greater than zero")

    peak_threshold = float(np.max(spectrum.amplitudes)) * threshold_ratio

    harmonics: list[float] = []

    for harmonic in range(
        1,
        max_harmonic + 1,
    ):
        target = fundamental_frequency * harmonic

        distances = np.abs(spectrum.frequencies - target)

        index = int(np.argmin(distances))

        if distances[index] <= tolerance_hz:
            if spectrum.amplitudes[index] >= peak_threshold:
                harmonics.append(float(spectrum.frequencies[index]))

    return harmonics
