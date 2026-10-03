from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from app.models.fbg import (
    FBGCalibration,
    FBGTrackingPoint,
    FBGTrackingResult,
)
from app.models.spectrum import Spectrum
from app.processing.fbg import (
    compare_series,
    delta_wavelength,
    detect_bragg_peak,
    detect_bragg_peaks,
    reduce_spectrum_noise,
    spectrum_metrics,
    track_bragg_wavelength,
    tracking_frequency,
    validate_against_labview,
)


def make_spectrum(
    center: float,
    *,
    noise: float = 0.0,
    seed: int = 7,
) -> Spectrum:
    wavelength = np.linspace(
        1549.0,
        1551.0,
        2001,
    )

    rng = np.random.default_rng(seed)

    intensity = np.exp(-0.5 * ((wavelength - center) / 0.025) ** 2)

    if noise:
        intensity = intensity + rng.normal(
            0.0,
            noise,
            wavelength.size,
        )

    return Spectrum(
        timestamp=datetime.now(UTC),
        device_id="fbg-001",
        wavelength=wavelength,
        intensity=intensity,
    )


def test_noise_reduction_preserves_wavelength_axis() -> None:
    spectrum = make_spectrum(
        1550.23,
        noise=0.02,
    )

    filtered = reduce_spectrum_noise(
        spectrum,
        window_length=11,
        polyorder=3,
    )

    assert np.array_equal(
        filtered.wavelength,
        spectrum.wavelength,
    )

    assert filtered.intensity.shape == spectrum.intensity.shape


def test_bragg_peak_detection_and_quadratic_refinement() -> None:
    spectrum = make_spectrum(
        1550.231,
    )

    result = detect_bragg_peaks(
        spectrum,
        prominence=0.1,
        noise_reduction=False,
    )

    assert result.peaks

    peak = detect_bragg_peak(
        spectrum,
        prominence=0.1,
        noise_reduction=False,
    )

    assert peak.wavelength_nm == pytest.approx(
        1550.231,
        abs=2e-4,
    )

    assert peak.intensity == pytest.approx(
        1.0,
        abs=1e-3,
    )


def test_tracking_and_delta_wavelength() -> None:
    base = datetime(
        2026,
        10,
        2,
        tzinfo=UTC,
    )

    spectra = []

    for index, center in enumerate(
        (
            1550.21,
            1550.24,
            1550.28,
            1550.32,
        )
    ):
        spectrum = make_spectrum(
            center,
        )

        spectrum.timestamp = base + timedelta(seconds=index)

        spectra.append(spectrum)

    tracking = track_bragg_wavelength(
        spectra,
        prominence=0.1,
        noise_reduction=False,
    )

    wavelengths = [point.wavelength_nm for point in tracking.points]

    shifts = [point.delta_wavelength_nm for point in tracking.points]

    assert wavelengths == pytest.approx(
        [
            1550.21,
            1550.24,
            1550.28,
            1550.32,
        ],
        abs=2e-4,
    )

    assert shifts == pytest.approx(
        [
            0.0,
            0.03,
            0.07,
            0.11,
        ],
        abs=2e-4,
    )

    assert delta_wavelength(
        wavelengths,
        reference_wavelength_nm=1550.21,
    ) == pytest.approx(
        [
            0.0,
            0.03,
            0.07,
            0.11,
        ],
        abs=2e-4,
    )


def test_fbg_physical_calibration() -> None:
    calibration = FBGCalibration(
        photoelastic_constant=0.22,
        thermal_expansion_coefficient_per_c=0.55e-6,
        thermo_optic_coefficient_per_c=8.6e-6,
    )

    reference = 1550.0
    strain = 100e-6
    delta_temperature = 0.0

    shift = reference * (
        calibration.strain_sensitivity * strain
        + calibration.temperature_sensitivity_per_c * delta_temperature
    )

    assert calibration.strain_from_shift(
        shift,
        reference,
    ) == pytest.approx(strain)

    assert calibration.microstrain_from_shift(
        shift,
        reference,
    ) == pytest.approx(100.0)


def test_temperature_calibration() -> None:
    calibration = FBGCalibration(
        photoelastic_constant=0.22,
        thermal_expansion_coefficient_per_c=0.55e-6,
        thermo_optic_coefficient_per_c=8.6e-6,
    )

    reference = 1550.0
    temperature = 20.0

    shift = reference * calibration.temperature_sensitivity_per_c * temperature

    assert calibration.temperature_from_shift(
        shift,
        reference,
    ) == pytest.approx(temperature)


def test_validation_metrics() -> None:
    reference = [
        1550.20,
        1550.25,
        1550.30,
    ]

    candidate = [
        1550.20,
        1550.26,
        1550.29,
    ]

    metric = compare_series(
        reference,
        candidate,
        name="wavelength_nm",
    )

    assert metric.absolute_error == pytest.approx(0.0066666667)

    assert metric.rmse == pytest.approx(np.sqrt((0.0**2 + 0.01**2 + (-0.01) ** 2) / 3))

    assert 0.0 < metric.relative_error
    assert metric.correlation > 0.98


def test_labview_validation_uses_common_quantities() -> None:
    report = validate_against_labview(
        {
            "wavelength_nm": [
                1550.20,
                1550.25,
            ],
            "rms": [
                0.5,
                0.6,
            ],
            "frequency_hz": [
                10.0,
                10.1,
            ],
        },
        {
            "wavelength_nm": [
                1550.21,
                1550.24,
            ],
            "rms": [
                0.5,
                0.59,
            ],
            "frequency_hz": [
                10.0,
                10.0,
            ],
        },
    )

    assert len(report.metrics) == 3

    assert report.by_name("wavelength_nm").rmse > 0


def test_spectrum_metrics_and_tracking_frequency() -> None:
    spectrum = make_spectrum(
        1550.23,
    )

    metrics = spectrum_metrics(
        spectrum,
        noise_reduction=False,
    )

    assert metrics.peak_wavelength_nm == pytest.approx(
        1550.23,
        abs=2e-4,
    )

    assert metrics.peak_amplitude == pytest.approx(
        1.0,
        abs=1e-3,
    )

    assert metrics.rms > 0.0

    base = datetime(
        2026,
        10,
        2,
        tzinfo=UTC,
    )

    values = 1550.23 + 0.01 * np.sin(2 * np.pi * 0.2 * np.arange(20))

    tracking = FBGTrackingResult(
        reference_wavelength_nm=1550.23,
        points=tuple(
            FBGTrackingPoint(
                timestamp=(base + timedelta(seconds=int(index))),
                wavelength_nm=float(value),
                delta_wavelength_nm=float(value - 1550.23),
                peak_intensity=1.0,
            )
            for index, value in enumerate(values)
        ),
    )

    assert tracking_frequency(tracking) == pytest.approx(
        0.2,
        abs=0.051,
    )


def test_invalid_calibration_is_rejected() -> None:
    with pytest.raises(ValueError):
        FBGCalibration(
            photoelastic_constant=1.0,
            thermal_expansion_coefficient_per_c=1e-6,
            thermo_optic_coefficient_per_c=8e-6,
        )
