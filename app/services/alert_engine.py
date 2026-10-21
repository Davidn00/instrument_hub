"""Pure rule evaluation for InstrumentHub measurements."""

import math
from typing import Any

from app.models.measurement import Measurement

# Each metric has aliases because devices may use different channel names.
METRIC_ALIASES: dict[str, set[str]] = {
    "temperature": {"temperature", "temp", "temperature_c"},
    "strain": {"strain", "microstrain", "strain_ue"},
    "signal_quality": {"signal_quality", "quality_score", "snr"},
}


def compare(value: float, operator: str, threshold: float) -> bool:
    """Apply an explicitly selected comparison operator."""

    if operator == "gt":
        return value > threshold
    if operator == "gte":
        return value >= threshold
    if operator == "lt":
        return value < threshold
    if operator == "lte":
        return value <= threshold

    raise ValueError(f"Unsupported alert operator: {operator}")


def metric_value(
    metric: str,
    measurement: Measurement,
) -> float | None:
    """Extract the value relevant to a rule, or None if unavailable."""

    channel = measurement.channel.strip().lower()
    metadata: dict[str, Any] = measurement.metadata

    if metric == "wavelength_drift":
        # Prefer an explicitly computed delta from the FBG processing stage.
        delta = metadata.get("delta_wavelength_nm")
        if isinstance(delta, (int, float)) and math.isfinite(float(delta)):
            return abs(float(delta))
        return None

    if metric == "signal_quality":
        # The domain quality label GOOD/BAD is categorical, not numeric.
        # Only evaluate a threshold if a numerical score is supplied.
        score = metadata.get("signal_quality", metadata.get("quality_score"))
        if isinstance(score, (int, float)) and math.isfinite(float(score)):
            return float(score)
        return None

    if channel not in METRIC_ALIASES.get(metric, {metric}):
        # Also accept an explicit measurement_type from instrument metadata.
        measurement_type = str(metadata.get("measurement_type", "")).strip().lower()
        if measurement_type not in METRIC_ALIASES.get(metric, {metric}):
            return None

    if not math.isfinite(measurement.value):
        return None

    return float(measurement.value)


def evaluate_rule(
    rule: Any,
    measurement: Measurement,
) -> dict[str, Any] | None:
    """Return an alert payload when a rule matches the measurement."""

    if not rule.enabled:
        return None

    if rule.device_id and rule.device_id != measurement.device_id:
        return None

    if rule.channel and rule.channel != measurement.channel:
        return None

    value = metric_value(rule.metric, measurement)
    if value is None:
        return None

    if not compare(value, rule.operator, rule.threshold):
        return None

    return {
        "rule_id": str(rule.id),
        "metric": rule.metric,
        "device_id": measurement.device_id,
        "channel": measurement.channel,
        "value": value,
        "threshold": rule.threshold,
        "operator": rule.operator,
        "severity": rule.severity,
        "message": (
            f"{rule.name}: {rule.metric}={value:g} {rule.operator} {rule.threshold:g}"
        ),
    }
