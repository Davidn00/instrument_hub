from typing import Literal

import numpy as np
from scipy import signal as scipy_signal

from app.processing.statistics import as_float_array


def moving_average(
    samples: np.ndarray | list[float] | tuple[float, ...],
    window_size: int,
) -> np.ndarray:
    """
    Apply a centered moving-average filter while preserving signal length.
    """

    array = as_float_array(samples)

    if window_size <= 0:
        raise ValueError("window_size must be greater than zero")

    if window_size > array.size:
        raise ValueError("window_size cannot exceed number of samples")

    kernel = (
        np.ones(
            window_size,
            dtype=float,
        )
        / window_size
    )

    return np.convolve(
        array,
        kernel,
        mode="same",
    )


def _validate_sampling_rate(
    sampling_rate: float,
) -> None:
    if sampling_rate <= 0:
        raise ValueError("sampling_rate must be greater than zero")


def _validate_cutoff(
    cutoff: float | tuple[float, float],
    sampling_rate: float,
) -> None:
    nyquist = sampling_rate / 2.0

    if isinstance(cutoff, tuple):
        low, high = cutoff

        if not 0 < low < high < nyquist:
            raise ValueError(
                "band-pass cutoff frequencies must satisfy 0 < low < high < Nyquist"
            )

        return

    if not 0 < cutoff < nyquist:
        raise ValueError("cutoff must be between 0 and the Nyquist frequency")


def butterworth_filter(
    samples: np.ndarray | list[float] | tuple[float, ...],
    sampling_rate: float,
    cutoff: float | tuple[float, float],
    *,
    btype: str = "lowpass",
    order: int = 4,
) -> np.ndarray:
    """
    Apply a zero-phase Butterworth filter.

    Supported types:
        lowpass
        highpass
        bandpass
    """

    array = as_float_array(samples)

    _validate_sampling_rate(sampling_rate)

    if order <= 0:
        raise ValueError("order must be greater than zero")

    normalized_type = btype.lower().replace("-", "")

    aliases = {
        "low": "lowpass",
        "high": "highpass",
        "band": "bandpass",
    }

    normalized_type = aliases.get(
        normalized_type,
        normalized_type,
    )

    if normalized_type not in {
        "lowpass",
        "highpass",
        "bandpass",
    }:
        raise ValueError("btype must be lowpass, highpass or bandpass")

    filter_type: Literal[
        "lowpass",
        "highpass",
        "bandpass",
    ] = normalized_type  # type: ignore[assignment]

    _validate_cutoff(
        cutoff,
        sampling_rate,
    )

    if normalized_type == "bandpass" and not isinstance(cutoff, tuple):
        raise ValueError("bandpass requires cutoff=(low, high)")

    if normalized_type != "bandpass" and isinstance(cutoff, tuple):
        raise ValueError("lowpass/highpass require a single cutoff frequency")

    sos = scipy_signal.butter(
        order,
        cutoff,
        btype=filter_type,
        fs=sampling_rate,
        output="sos",
    )

    try:
        return scipy_signal.sosfiltfilt(
            sos,
            array,
        )
    except ValueError as exc:
        raise ValueError(
            "signal is too short for the requested Butterworth filter"
        ) from exc


def low_pass_filter(
    samples: np.ndarray | list[float] | tuple[float, ...],
    sampling_rate: float,
    cutoff: float,
    *,
    order: int = 4,
) -> np.ndarray:
    return butterworth_filter(
        samples,
        sampling_rate,
        cutoff,
        btype="lowpass",
        order=order,
    )


def high_pass_filter(
    samples: np.ndarray | list[float] | tuple[float, ...],
    sampling_rate: float,
    cutoff: float,
    *,
    order: int = 4,
) -> np.ndarray:
    return butterworth_filter(
        samples,
        sampling_rate,
        cutoff,
        btype="highpass",
        order=order,
    )


def band_pass_filter(
    samples: np.ndarray | list[float] | tuple[float, ...],
    sampling_rate: float,
    low_cutoff: float,
    high_cutoff: float,
    *,
    order: int = 4,
) -> np.ndarray:
    return butterworth_filter(
        samples,
        sampling_rate,
        (low_cutoff, high_cutoff),
        btype="bandpass",
        order=order,
    )


def notch_filter(
    samples: np.ndarray | list[float] | tuple[float, ...],
    sampling_rate: float,
    frequency: float,
    *,
    quality_factor: float = 30.0,
) -> np.ndarray:
    """
    Apply a narrow-band IIR notch filter.

    Useful for removing mains interference such as 50/60 Hz.
    """

    array = as_float_array(samples)

    _validate_sampling_rate(sampling_rate)

    nyquist = sampling_rate / 2.0

    if not 0 < frequency < nyquist:
        raise ValueError("frequency must be between 0 and the Nyquist frequency")

    if quality_factor <= 0:
        raise ValueError("quality_factor must be greater than zero")

    b, a = scipy_signal.iirnotch(
        w0=frequency,
        Q=quality_factor,
        fs=sampling_rate,
    )

    try:
        return scipy_signal.filtfilt(
            b,
            a,
            array,
        )
    except ValueError as exc:
        raise ValueError("signal is too short for the requested notch filter") from exc
