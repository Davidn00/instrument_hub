from abc import ABC, abstractmethod
from typing import Any

from app.models.measurement import Measurement


class Instrument(ABC):
    """Stable hardware-independent interface for every InstrumentHub instrument."""

    def __init__(
        self,
        device_id: str,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not device_id:
            raise ValueError("device_id cannot be empty")
        if not name:
            raise ValueError("name cannot be empty")

        self.device_id = device_id
        self.name = name
        self.metadata = metadata or {}
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    @abstractmethod
    async def connect(self) -> None:
        """Open the instrument connection."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the instrument connection."""

    @abstractmethod
    async def read(self) -> Measurement:
        """Read one domain measurement."""

    async def __aenter__(self) -> "Instrument":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> None:
        await self.disconnect()


# Backward-compatible name used by Stage 2.
InstrumentDevice = Instrument
