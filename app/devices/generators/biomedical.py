import numpy as np


def generate_ecg(
    sampling_rate: float,
    duration: float,
    heart_rate: float = 72.0,
    amplitude: float = 1.0,
    noise_amplitude: float = 0.0,
    seed: int | None = None,
) -> np.ndarray:
    """
    Generate a synthetic ECG-like waveform.

    The waveform is intentionally simplified and is intended
    for simulation and software testing, not clinical use.
    """

    if sampling_rate <= 0:
        raise ValueError("sampling_rate must be greater than zero")

    if duration <= 0:
        raise ValueError("duration must be greater than zero")

    if heart_rate <= 0:
        raise ValueError("heart_rate must be greater than zero")

    if amplitude < 0:
        raise ValueError("amplitude cannot be negative")

    sample_count = int(duration * sampling_rate)
    time = np.arange(sample_count) / sampling_rate

    beat_frequency = heart_rate / 60.0
    phase = (time * beat_frequency) % 1.0

    p_wave = 0.15 * np.exp(-((phase - 0.20) ** 2) / (2 * 0.025**2))

    q_wave = -0.15 * np.exp(-((phase - 0.38) ** 2) / (2 * 0.012**2))

    r_wave = 1.00 * np.exp(-((phase - 0.40) ** 2) / (2 * 0.010**2))

    s_wave = -0.25 * np.exp(-((phase - 0.43) ** 2) / (2 * 0.014**2))

    t_wave = 0.30 * np.exp(-((phase - 0.65) ** 2) / (2 * 0.060**2))

    signal = amplitude * (p_wave + q_wave + r_wave + s_wave + t_wave)

    if noise_amplitude > 0:
        rng = np.random.default_rng(seed)
        signal += rng.normal(
            0.0,
            noise_amplitude,
            sample_count,
        )

    return signal


def generate_emg(
    sampling_rate: float,
    duration: float,
    amplitude: float = 1.0,
    burst_frequency: float = 50.0,
    noise_amplitude: float = 0.05,
    seed: int | None = None,
) -> np.ndarray:
    """
    Generate a synthetic EMG-like signal.
    """

    if sampling_rate <= 0:
        raise ValueError("sampling_rate must be greater than zero")

    if duration <= 0:
        raise ValueError("duration must be greater than zero")

    if amplitude < 0:
        raise ValueError("amplitude cannot be negative")

    if burst_frequency <= 0:
        raise ValueError("burst_frequency must be greater than zero")

    sample_count = int(duration * sampling_rate)

    rng = np.random.default_rng(seed)

    broadband_noise = rng.normal(
        0.0,
        amplitude,
        sample_count,
    )

    time = np.arange(sample_count) / sampling_rate

    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * burst_frequency * time)

    signal = broadband_noise * envelope

    if noise_amplitude > 0:
        signal += rng.normal(
            0.0,
            noise_amplitude,
            sample_count,
        )

    return signal
