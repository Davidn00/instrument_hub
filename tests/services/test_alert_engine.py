"""Unit tests for threshold evaluation."""

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from app.models.measurement import Measurement
from app.services.alert_engine import compare, evaluate_rule


@pytest.mark.parametrize(
    ("value", "operator", "threshold", "expected"),
    [
        (31.0, "gt", 30.0, True),
        (30.0, "gt", 30.0, False),
        (30.0, "gte", 30.0, True),
        (20.0, "lt", 25.0, True),
        (25.0, "lte", 25.0, True),
    ],
)
def test_compare(
    value: float,
    operator: str,
    threshold: float,
    expected: bool,
) -> None:
    assert compare(value, operator, threshold) is expected


def make_measurement(
    value: float,
    channel: str = "temperature",
    metadata: dict | None = None,
) -> Measurement:
    """Create a normalized domain measurement for a unit test."""

    return Measurement(
        timestamp=datetime.now(UTC),
        device_id="temperature-01",
        channel=channel,
        value=value,
        unit="°C",
        quality="GOOD",
        metadata=metadata or {},
    )


def make_rule(**overrides: object) -> SimpleNamespace:
    """Build a lightweight rule without needing a database session."""

    values = {
        "id": "rule-1",
        "name": "High temperature",
        "metric": "temperature",
        "operator": "gt",
        "threshold": 30.0,
        "device_id": None,
        "channel": None,
        "severity": "WARNING",
        "enabled": True,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_temperature_above_threshold_triggers_alert() -> None:
    result = evaluate_rule(
        make_rule(),
        make_measurement(35.0),
    )

    assert result is not None
    assert result["metric"] == "temperature"
    assert result["value"] == 35.0


def test_temperature_below_threshold_does_not_trigger() -> None:
    result = evaluate_rule(
        make_rule(),
        make_measurement(25.0),
    )

    assert result is None


def test_rule_can_filter_by_device() -> None:
    result = evaluate_rule(
        make_rule(device_id="another-device"),
        make_measurement(35.0),
    )

    assert result is None


def test_disabled_rule_is_ignored() -> None:
    result = evaluate_rule(
        make_rule(enabled=False),
        make_measurement(35.0),
    )

    assert result is None


def test_strain_metric_uses_channel_alias() -> None:
    rule = make_rule(
        metric="strain",
        threshold=100.0,
        operator="gt",
    )

    result = evaluate_rule(
        rule,
        make_measurement(150.0, channel="strain"),
    )

    assert result is not None


def test_wavelength_drift_requires_computed_delta() -> None:
    rule = make_rule(metric="wavelength_drift", threshold=0.2)

    without_delta = evaluate_rule(
        rule,
        make_measurement(1550.0, channel="wavelength"),
    )
    with_delta = evaluate_rule(
        rule,
        make_measurement(
            1550.0,
            channel="wavelength",
            metadata={"delta_wavelength_nm": 0.35},
        ),
    )

    assert without_delta is None
    assert with_delta is not None
    assert with_delta["value"] == pytest.approx(0.35)


def test_signal_quality_requires_numeric_score() -> None:
    rule = make_rule(
        metric="signal_quality",
        operator="lt",
        threshold=0.8,
    )

    categorical_only = evaluate_rule(
        rule,
        make_measurement(1.0, metadata={}),
    )
    low_score = evaluate_rule(
        rule,
        make_measurement(
            1.0,
            metadata={"signal_quality": 0.4},
        ),
    )

    assert categorical_only is None
    assert low_score is not None
