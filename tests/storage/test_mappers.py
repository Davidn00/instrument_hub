from datetime import UTC, datetime

import numpy as np

from app.models.measurement import Measurement
from app.models.spectrum import Spectrum
from app.storage.mappers import (
    measurement_to_record,
    record_to_measurement,
    record_to_spectrum,
    spectrum_to_record,
)


def test_measurement_mapping_round_trip() -> None:
    measurement = Measurement(
        timestamp=datetime.now(UTC),
        device_id="device-01",
        channel="channel-01",
        value=12.5,
        unit="V",
        quality="GOOD",
        metadata={
            "measurement_type": "voltage",
        },
    )

    record = measurement_to_record(measurement)

    restored = record_to_measurement(record)

    assert restored.device_id == measurement.device_id
    assert restored.channel == measurement.channel
    assert restored.value == measurement.value
    assert restored.unit == measurement.unit
    assert restored.quality == measurement.quality
    assert restored.metadata == measurement.metadata


def test_spectrum_mapping_round_trip() -> None:
    spectrum = Spectrum(
        timestamp=datetime.now(UTC),
        device_id="ibsen-01",
        wavelength=np.array([1549.0, 1550.0, 1551.0]),
        intensity=np.array([10.0, 100.0, 20.0]),
    )

    record = spectrum_to_record(spectrum)

    restored = record_to_spectrum(record)

    np.testing.assert_allclose(
        restored.wavelength,
        spectrum.wavelength,
    )

    np.testing.assert_allclose(
        restored.intensity,
        spectrum.intensity,
    )

    assert restored.device_id == spectrum.device_id
