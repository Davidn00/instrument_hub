from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.models.measurement import Measurement


@dataclass(slots=True, frozen=True)
class Frame:
    """A validated transport frame extracted from raw bytes."""

    raw: bytes
    received_at: datetime
    protocol: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.received_at.tzinfo is None:
            object.__setattr__(
                self,
                "received_at",
                self.received_at.replace(tzinfo=UTC),
            )

        if not self.raw:
            raise ValueError("frame raw data cannot be empty")


class FrameDecoder(ABC):
    """Converts an arbitrary byte stream into complete frames."""

    @abstractmethod
    def feed(self, data: bytes) -> list[Frame]:
        """Consume bytes and return every complete frame available."""

    @abstractmethod
    def reset(self) -> None:
        """Clear any partial frame currently buffered."""


class MeasurementParser(ABC):
    """Converts protocol frames into domain measurements."""

    @abstractmethod
    def parse(
        self,
        frame: Frame,
    ) -> list[Measurement]:
        """Parse one frame into zero or more Measurement objects."""


class ProtocolParser:
    """Pipeline: raw bytes -> frames -> parser -> measurements."""

    def __init__(
        self,
        decoder: FrameDecoder,
        parser: MeasurementParser,
    ) -> None:
        self.decoder = decoder
        self.parser = parser

    def feed(
        self,
        data: bytes,
    ) -> list[Measurement]:
        measurements: list[Measurement] = []

        for frame in self.decoder.feed(data):
            measurements.extend(self.parser.parse(frame))

        return measurements

    def reset(self) -> None:
        self.decoder.reset()
