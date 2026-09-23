from abc import ABC, abstractmethod
from typing import Any

from app.models.measurement import Measurement


class InstrumentDevice(ABC):
    """
    Abstract interface for every InstrumentHub device.
    """

    def __init__(
        self,
        device_id: str,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.device_id = device_id
        self.name = name
        self.metadata = metadata or {}
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    @abstractmethod
    async def connect(self) -> None:
        """Connect the device."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect the device."""

    @abstractmethod
    async def read(self) -> Measurement:
        """Read one measurement from the device."""

    async def __aenter__(self) -> "InstrumentDevice":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> None:
        await self.disconnect()
