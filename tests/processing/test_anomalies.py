import numpy as np
import pytest

from app.processing.anomalies import (
    iqr_anomalies,
    rolling_zscore_anomalies,
    threshold_anomalies,
    zscore_anomalies,
)


def test_threshold_anomalies() -> None:
    result = threshold_anomalies(
        [1.0, 2.0, 10.0, -5.0],
        lower=0.0,
        upper=5.0,
    )

    assert np.array_equal(
        result,
        [
            False,
            False,
            True,
            True,
        ],
    )


def test_zscore_anomalies() -> None:
    result = zscore_anomalies(
        [0, 0, 0, 0, 10],
        threshold=1.5,
    )

    assert result[-1]


def test_iqr_anomalies() -> None:
    result = iqr_anomalies([1, 1, 1, 1, 1, 20])

    assert result[-1]


def test_rolling_zscore_anomalies() -> None:
    result = rolling_zscore_anomalies(
        [1, 1, 1, 1, 1, 10],
        window_size=5,
        threshold=1.5,
        min_periods=3,
    )

    assert result[-1]


def test_invalid_threshold_configuration() -> None:
    with pytest.raises(ValueError):
        threshold_anomalies([1, 2, 3])

    with pytest.raises(ValueError):
        zscore_anomalies(
            [1, 2, 3],
            threshold=0,
        )
