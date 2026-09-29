from datetime import UTC, datetime

import pytest

from app.models.measurement import Measurement


def test_measurement_uses_stage4_contract() -> None:
    measurement = Measurement(
        timestamp=datetime.now(UTC),
        device_id="dev-001",
        channel="ECG-I",
        value=1.2,
        unit="mV",
        quality="GOOD",
        metadata={
            "measurement_type": "ecg",
        },
    )

    assert measurement.channel == "ECG-I"
    assert measurement.quality == "GOOD"
    assert measurement.sensor_id == "ECG-I"
    assert measurement.measurement_type == "ecg"


def test_measurement_rejects_invalid_quality() -> None:
    with pytest.raises(ValueError):
        Measurement(
            timestamp=datetime.now(UTC),
            device_id="dev-001",
            channel="CH1",
            value=1.0,
            unit="V",
            quality="INVALID",
        )
