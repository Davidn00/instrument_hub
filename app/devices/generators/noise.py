import numpy as np


def generate_noise(
    amplitude: float,
    sampling_rate: float,
    duration: float,
    seed: int | None = None,
) -> np.ndarray:
    """
    Generate Gaussian white noise.
    """

    if amplitude < 0:
        raise ValueError("amplitude cannot be negative")

    if sampling_rate <= 0:
        raise ValueError("sampling_rate must be greater than zero")

    if duration <= 0:
        raise ValueError("duration must be greater than zero")

    sample_count = int(duration * sampling_rate)

    if sample_count <= 0:
        raise ValueError("duration produces zero samples")

    rng = np.random.default_rng(seed)

    return rng.normal(
        loc=0.0,
        scale=amplitude,
        size=sample_count,
    )
