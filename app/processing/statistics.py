from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class SignalStatistics:
    """Descriptive statistics for a one-dimensional numeric signal."""

    mean: float
    standard_deviation: float
    rms: float
    minimum: float
    maximum: float
    number_of_samples: int


def as_float_array(
    samples: np.ndarray | list[float] | tuple[float, ...],
) -> np.ndarray:
    """
    Validate and convert samples to a one-dimensional float array.
    """

    array = np.asarray(
        samples,
        dtype=float,
    )

    if array.ndim != 1:
        raise ValueError("samples must be a one-dimensional array")

    if array.size == 0:
        raise ValueError("samples cannot be empty")

    if not np.all(np.isfinite(array)):
        raise ValueError("samples must contain only finite values")

    return array


def normalize_zscore(
    samples: np.ndarray | list[float] | tuple[float, ...],
) -> np.ndarray:
    """
    Normalize a signal using z-score normalization.
    """

    array = as_float_array(samples)

    mean = float(np.mean(array))

    standard_deviation = float(np.std(array))

    if standard_deviation == 0:
        return np.zeros_like(array)

    return (array - mean) / standard_deviation


def normalize_minmax(
    samples: np.ndarray | list[float] | tuple[float, ...],
    *,
    feature_min: float = 0.0,
    feature_max: float = 1.0,
) -> np.ndarray:
    """
    Scale a signal linearly into [feature_min, feature_max].
    """

    if feature_min >= feature_max:
        raise ValueError("feature_min must be less than feature_max")

    array = as_float_array(samples)

    source_min = float(np.min(array))

    source_max = float(np.max(array))

    if source_max == source_min:
        return np.full_like(
            array,
            feature_min,
        )

    scaled = (array - source_min) / (source_max - source_min)

    return feature_min + scaled * (feature_max - feature_min)


def mean(
    samples: np.ndarray | list[float] | tuple[float, ...],
) -> float:
    return float(np.mean(as_float_array(samples)))


def standard_deviation(
    samples: np.ndarray | list[float] | tuple[float, ...],
    *,
    ddof: int = 0,
) -> float:
    array = as_float_array(samples)

    if ddof < 0 or ddof >= array.size:
        raise ValueError("ddof must be between 0 and number_of_samples - 1")

    return float(
        np.std(
            array,
            ddof=ddof,
        )
    )


def rms(
    samples: np.ndarray | list[float] | tuple[float, ...],
) -> float:
    """
    Root Mean Square.
    """

    array = as_float_array(samples)

    return float(np.sqrt(np.mean(np.square(array))))


def minimum(
    samples: np.ndarray | list[float] | tuple[float, ...],
) -> float:
    return float(np.min(as_float_array(samples)))


def maximum(
    samples: np.ndarray | list[float] | tuple[float, ...],
) -> float:
    return float(np.max(as_float_array(samples)))


def statistics(
    samples: np.ndarray | list[float] | tuple[float, ...],
    *,
    ddof: int = 0,
) -> SignalStatistics:
    """
    Calculate the main descriptive statistics for a signal.
    """

    array = as_float_array(samples)

    return SignalStatistics(
        mean=float(np.mean(array)),
        standard_deviation=standard_deviation(
            array,
            ddof=ddof,
        ),
        rms=float(np.sqrt(np.mean(np.square(array)))),
        minimum=float(np.min(array)),
        maximum=float(np.max(array)),
        number_of_samples=int(array.size),
    )


def sliding_windows(
    samples: np.ndarray | list[float] | tuple[float, ...],
    window_size: int,
    *,
    step: int = 1,
) -> np.ndarray:
    """
    Return overlapping windows without padding the signal.
    """

    array = as_float_array(samples)

    if window_size <= 0:
        raise ValueError("window_size must be greater than zero")

    if step <= 0:
        raise ValueError("step must be greater than zero")

    if window_size > array.size:
        raise ValueError("window_size cannot exceed number of samples")

    windows = np.lib.stride_tricks.sliding_window_view(
        array,
        window_shape=window_size,
    )

    return windows[::step].copy()
