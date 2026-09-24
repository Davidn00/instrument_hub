from collections.abc import Callable
from typing import Any

import numpy as np

from app.devices.generators.biomedical import (
    generate_ecg,
    generate_emg,
)
from app.devices.generators.noise import generate_noise
from app.devices.generators.optical import generate_fbg_spectrum
from app.devices.generators.sine import generate_sine


def generate_signal(
    signal_type: str,
    **parameters: Any,
) -> np.ndarray:
    """
    Generic signal generation entry point.
    """

    generators: dict[str, Callable[..., np.ndarray]] = {
        "sine": generate_sine,
        "noise": generate_noise,
        "ecg": generate_ecg,
        "emg": generate_emg,
    }

    if signal_type == "fbg_spectrum":
        _, spectrum = generate_fbg_spectrum(**parameters)
        return spectrum

    try:
        generator = generators[signal_type]
    except KeyError as exc:
        raise ValueError(f"Unsupported signal type: {signal_type}") from exc

    return generator(**parameters)
