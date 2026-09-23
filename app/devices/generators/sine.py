import numpy as np


def generate_sine(
    frequency: float,
    amplitude: float,
    sampling_rate: float,
    duration: float,
    phase: float = 0.0,
    offset: float = 0.0,
) -> np.ndarray:
    """
    Generate a sinusoidal signal.
    """

    if frequency < 0:
        raise ValueError("frequency cannot be negative")

    if amplitude < 0:
        raise ValueError("amplitude cannot be negative")

    if sampling_rate <= 0:
        raise ValueError("sampling_rate must be greater than zero")

    if duration <= 0:
        raise ValueError("duration must be greater than zero")

    sample_count = int(duration * sampling_rate)

    if sample_count <= 0:
        raise ValueError("duration produces zero samples")

    time = np.arange(sample_count) / sampling_rate

    return offset + amplitude * np.sin(2 * np.pi * frequency * time + phase)
