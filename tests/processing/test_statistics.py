import numpy as np
import pytest

from app.processing.statistics import (
    normalize_minmax,
    normalize_zscore,
    sliding_windows,
    statistics,
)


def test_statistics_returns_expected_values() -> None:
    result = statistics([1.0, 2.0, 3.0, 4.0])

    assert result.mean == pytest.approx(2.5)

    assert result.standard_deviation == pytest.approx(np.std([1, 2, 3, 4]))

    assert result.rms == pytest.approx(np.sqrt(7.5))

    assert result.minimum == 1.0
    assert result.maximum == 4.0
    assert result.number_of_samples == 4


def test_zscore_normalization() -> None:
    result = normalize_zscore([1.0, 2.0, 3.0])

    assert np.mean(result) == pytest.approx(0.0)
    assert np.std(result) == pytest.approx(1.0)


def test_minmax_normalization() -> None:
    result = normalize_minmax(
        [10.0, 20.0, 30.0],
        feature_min=-1.0,
        feature_max=1.0,
    )

    assert np.allclose(
        result,
        [-1.0, 0.0, 1.0],
    )


def test_constant_zscore_signal_is_zero() -> None:
    assert np.allclose(
        normalize_zscore([5.0, 5.0, 5.0]),
        [0.0, 0.0, 0.0],
    )


def test_sliding_windows() -> None:
    result = sliding_windows(
        [1, 2, 3, 4, 5],
        3,
        step=2,
    )

    assert np.array_equal(
        result,
        [
            [1, 2, 3],
            [3, 4, 5],
        ],
    )


def test_invalid_statistics_input() -> None:
    with pytest.raises(ValueError):
        statistics([])

    with pytest.raises(ValueError):
        sliding_windows(
            [1, 2],
            3,
        )
