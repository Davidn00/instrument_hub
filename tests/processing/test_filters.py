import numpy as np
import pytest

from app.processing.filters import (
    band_pass_filter,
    high_pass_filter,
    low_pass_filter,
    moving_average,
    notch_filter,
)


def test_moving_average_preserves_length() -> None:
    result = moving_average(
        [1, 2, 3, 4, 5],
        3,
    )

    assert len(result) == 5
    assert result[2] == pytest.approx(3.0)


def test_low_pass_filter_preserves_signal_shape() -> None:
    sampling_rate = 1000.0

    time = np.arange(2000) / sampling_rate

    samples = np.sin(2 * np.pi * 10 * time) + 0.5 * np.sin(2 * np.pi * 200 * time)

    result = low_pass_filter(
        samples,
        sampling_rate,
        50.0,
    )

    assert result.shape == samples.shape


def test_high_pass_filter_preserves_signal_shape() -> None:
    sampling_rate = 1000.0

    time = np.arange(2000) / sampling_rate

    samples = np.sin(2 * np.pi * 10 * time) + 0.5 * np.sin(2 * np.pi * 200 * time)

    result = high_pass_filter(
        samples,
        sampling_rate,
        50.0,
    )

    assert result.shape == samples.shape


def test_band_pass_filter_preserves_signal_shape() -> None:
    sampling_rate = 1000.0

    time = np.arange(2000) / sampling_rate

    samples = np.sin(2 * np.pi * 10 * time) + np.sin(2 * np.pi * 100 * time)

    result = band_pass_filter(
        samples,
        sampling_rate,
        80.0,
        120.0,
    )

    assert result.shape == samples.shape


def test_notch_filter_preserves_signal_shape() -> None:
    sampling_rate = 1000.0

    time = np.arange(2000) / sampling_rate

    samples = np.sin(2 * np.pi * 50 * time)

    result = notch_filter(
        samples,
        sampling_rate,
        50.0,
    )

    assert result.shape == samples.shape


def test_invalid_cutoff_is_rejected() -> None:
    with pytest.raises(ValueError):
        low_pass_filter(
            [1, 2, 3, 4, 5],
            100.0,
            60.0,
        )
