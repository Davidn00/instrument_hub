import numpy as np
import pytest

from app.processing.spectral import (
    detect_harmonics,
    dominant_frequency,
    fft_spectrum,
    power_spectral_density,
)


def make_signal() -> tuple[np.ndarray, float]:
    sampling_rate = 1000.0

    time = np.arange(2000) / sampling_rate

    samples = np.sin(2 * np.pi * 50 * time) + 0.5 * np.sin(2 * np.pi * 100 * time)

    return samples, sampling_rate


def test_fft_detects_expected_frequency() -> None:
    samples, sampling_rate = make_signal()

    spectrum = fft_spectrum(
        samples,
        sampling_rate,
    )

    assert dominant_frequency(
        samples,
        sampling_rate,
    ) == pytest.approx(50.0)

    assert spectrum.frequencies.shape == spectrum.amplitudes.shape


def test_psd_returns_frequency_and_power_arrays() -> None:
    samples, sampling_rate = make_signal()

    result = power_spectral_density(
        samples,
        sampling_rate,
        nperseg=500,
    )

    assert result.frequencies.shape == result.power.shape

    assert result.frequencies.size > 0


def test_harmonics_are_detected() -> None:
    samples, sampling_rate = make_signal()

    harmonics = detect_harmonics(
        samples,
        sampling_rate,
        fundamental_frequency=50.0,
        max_harmonic=2,
        threshold_ratio=0.1,
    )

    assert harmonics == pytest.approx([50.0, 100.0])


def test_invalid_sampling_rate_is_rejected() -> None:
    with pytest.raises(ValueError):
        fft_spectrum(
            [1, 2, 3],
            0,
        )
