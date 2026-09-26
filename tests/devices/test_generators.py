import numpy as np
import pytest

from app.devices.generators import (
    generate_ecg,
    generate_emg,
    generate_fbg_spectrum,
    generate_noise,
    generate_sine,
)


def test_generate_sine_length() -> None:
    signal = generate_sine(
        frequency=10.0,
        amplitude=1.0,
        sampling_rate=1000.0,
        duration=2.0,
    )

    assert len(signal) == 2000


def test_generate_sine_amplitude() -> None:
    signal = generate_sine(
        frequency=10.0,
        amplitude=2.0,
        sampling_rate=1000.0,
        duration=1.0,
    )

    assert np.max(np.abs(signal)) <= 2.0


def test_generate_noise_reproducible() -> None:
    first = generate_noise(
        amplitude=1.0,
        sampling_rate=100.0,
        duration=1.0,
        seed=42,
    )

    second = generate_noise(
        amplitude=1.0,
        sampling_rate=100.0,
        duration=1.0,
        seed=42,
    )

    np.testing.assert_array_equal(first, second)


def test_generate_ecg_length() -> None:
    signal = generate_ecg(
        sampling_rate=500.0,
        duration=10.0,
    )

    assert len(signal) == 5000


def test_generate_emg_length() -> None:
    signal = generate_emg(
        sampling_rate=1000.0,
        duration=5.0,
    )

    assert len(signal) == 5000


def test_generate_fbg_spectrum() -> None:
    wavelengths, spectrum = generate_fbg_spectrum(
        points=1000,
    )

    assert len(wavelengths) == 1000
    assert len(spectrum) == 1000
    assert wavelengths[0] < wavelengths[-1]


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "frequency": 10.0,
            "amplitude": 1.0,
            "sampling_rate": 0.0,
            "duration": 1.0,
        },
        {
            "frequency": 10.0,
            "amplitude": 1.0,
            "sampling_rate": 1000.0,
            "duration": 0.0,
        },
    ],
)
def test_generate_sine_rejects_invalid_parameters(
    kwargs: dict[str, float],
) -> None:
    with pytest.raises(ValueError):
        generate_sine(**kwargs)
