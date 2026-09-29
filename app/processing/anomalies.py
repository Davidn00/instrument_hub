import numpy as np

from app.processing.statistics import as_float_array


def threshold_anomalies(
    samples: np.ndarray | list[float] | tuple[float, ...],
    *,
    lower: float | None = None,
    upper: float | None = None,
) -> np.ndarray:
    """
    Flag samples outside configured absolute limits.
    """

    if lower is None and upper is None:
        raise ValueError("at least one threshold must be provided")

    if lower is not None and upper is not None and lower > upper:
        raise ValueError("lower cannot be greater than upper")

    array = as_float_array(samples)

    mask = np.zeros(
        array.size,
        dtype=bool,
    )

    if lower is not None:
        mask |= array < lower

    if upper is not None:
        mask |= array > upper

    return mask


def zscore_anomalies(
    samples: np.ndarray | list[float] | tuple[float, ...],
    *,
    threshold: float = 3.0,
) -> np.ndarray:
    """
    Flag samples whose absolute z-score exceeds threshold.
    """

    if threshold <= 0:
        raise ValueError("threshold must be greater than zero")

    array = as_float_array(samples)

    mean = np.mean(array)

    standard_deviation = np.std(array)

    if standard_deviation == 0:
        return np.zeros(
            array.size,
            dtype=bool,
        )

    zscores = np.abs((array - mean) / standard_deviation)

    return np.asarray(
        zscores > threshold,
        dtype=bool,
    )


def iqr_anomalies(
    samples: np.ndarray | list[float] | tuple[float, ...],
    *,
    multiplier: float = 1.5,
) -> np.ndarray:
    """
    Flag samples outside Tukey's IQR fences.
    """

    if multiplier < 0:
        raise ValueError("multiplier cannot be negative")

    array = as_float_array(samples)

    q1, q3 = np.percentile(
        array,
        [25.0, 75.0],
    )

    iqr = q3 - q1

    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr

    return np.asarray(
        (array < lower) | (array > upper),
        dtype=bool,
    )


def rolling_zscore_anomalies(
    samples: np.ndarray | list[float] | tuple[float, ...],
    window_size: int,
    *,
    threshold: float = 3.0,
    min_periods: int | None = None,
) -> np.ndarray:
    """
    Flag samples using statistics from previous samples.

    The current sample is intentionally excluded from the rolling
    reference window. This makes the method useful for detecting
    sudden changes in streaming data.
    """

    if window_size <= 1:
        raise ValueError("window_size must be greater than one")

    if threshold <= 0:
        raise ValueError("threshold must be greater than zero")

    array = as_float_array(samples)

    if min_periods is None:
        min_periods = window_size

    if min_periods <= 0 or min_periods > window_size:
        raise ValueError("min_periods must be between 1 and window_size")

    result = np.zeros(
        array.size,
        dtype=bool,
    )

    for index in range(array.size):
        start = max(
            0,
            index - window_size,
        )

        window = array[start:index]

        if window.size < min_periods:
            continue

        mean = np.mean(window)

        standard_deviation = np.std(window)

        if standard_deviation == 0:
            result[index] = not np.isclose(
                array[index],
                mean,
            )
            continue

        result[index] = abs((array[index] - mean) / standard_deviation) > threshold

    return result
