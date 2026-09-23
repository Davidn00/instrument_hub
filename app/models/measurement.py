from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class Measurement:
    """
    Represents one measurement produced by an instrument or sensor.
    """

    timestamp: datetime
    value: float
    unit: str
    sensor_id: str
    device_id: str
    measurement_type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=UTC)

        if not self.sensor_id:
            raise ValueError("sensor_id cannot be empty")

        if not self.device_id:
            raise ValueError("device_id cannot be empty")

        if not self.measurement_type:
            raise ValueError("measurement_type cannot be empty")

        if not self.unit:
            raise ValueError("unit cannot be empty")
