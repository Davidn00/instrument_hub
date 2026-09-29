from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

VALID_QUALITY = {"GOOD", "SUSPECT", "BAD", "UNKNOWN"}


@dataclass(slots=True, init=False)
class Measurement:
    """
    Standard domain measurement.

    Canonical fields:
    timestamp, device_id, channel, value, unit, quality, metadata

    sensor_id and measurement_type are accepted as legacy constructor
    arguments and exposed as compatibility properties for earlier stages.
    """

    timestamp: datetime
    device_id: str
    channel: str
    value: float
    unit: str
    quality: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        timestamp: datetime,
        device_id: str,
        channel: str | None = None,
        value: float = 0.0,
        unit: str = "",
        quality: str = "GOOD",
        metadata: dict[str, Any] | None = None,
        *,
        sensor_id: str | None = None,
        measurement_type: str | None = None,
    ) -> None:
        resolved_channel = channel or sensor_id

        if resolved_channel is None:
            raise ValueError("channel cannot be empty")

        resolved_metadata = dict(metadata or {})

        if measurement_type is not None:
            resolved_metadata.setdefault(
                "measurement_type",
                measurement_type,
            )

        self.timestamp = timestamp
        self.device_id = device_id
        self.channel = resolved_channel
        self.value = float(value)
        self.unit = unit
        self.quality = quality
        self.metadata = resolved_metadata

        self.__post_init__()

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=UTC)

        if not self.device_id:
            raise ValueError("device_id cannot be empty")

        if not self.channel:
            raise ValueError("channel cannot be empty")

        if not self.unit:
            raise ValueError("unit cannot be empty")

        if self.quality not in VALID_QUALITY:
            raise ValueError(f"quality must be one of {sorted(VALID_QUALITY)}")

    @property
    def sensor_id(self) -> str:
        """
        Backward-compatible alias for the previous Stage 2/3 contract.
        """
        return self.channel

    @property
    def measurement_type(self) -> str:
        """
        Backward-compatible alias stored in metadata.
        """
        return str(
            self.metadata.get(
                "measurement_type",
                self.channel,
            )
        )
