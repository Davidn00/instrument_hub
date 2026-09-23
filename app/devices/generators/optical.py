import numpy as np


def generate_fbg_spectrum(
    center_wavelength: float = 1550.23,
    wavelength_start: float = 1548.0,
    wavelength_end: float = 1552.0,
    points: int = 2000,
    amplitude: float = 1.0,
    linewidth: float = 0.08,
    noise_amplitude: float = 0.0,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a synthetic Fiber Bragg Grating spectrum.

    Returns:
        wavelengths_nm
        intensities
    """

    if wavelength_start >= wavelength_end:
        raise ValueError("wavelength_start must be lower than wavelength_end")

    if points <= 1:
        raise ValueError("points must be greater than one")

    if linewidth <= 0:
        raise ValueError("linewidth must be greater than zero")

    if amplitude < 0:
        raise ValueError("amplitude cannot be negative")

    wavelengths = np.linspace(
        wavelength_start,
        wavelength_end,
        points,
    )

    spectrum = amplitude * np.exp(
        -0.5 * ((wavelengths - center_wavelength) / linewidth) ** 2
    )

    if noise_amplitude > 0:
        rng = np.random.default_rng(seed)

        spectrum += rng.normal(
            0.0,
            noise_amplitude,
            points,
        )

    return wavelengths, spectrum
