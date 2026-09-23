from abc import abstractmethod
from typing import Any

from app.devices.base import InstrumentDevice
from app.models.measurement import Measurement


class SimulatedDevice(InstrumentDevice):
    """
    Base class for virtual instruments.
    """

    def __init__(
        self,
        device_id: str,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            device_id=device_id,
            name=name,
            metadata=metadata,
        )

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def read(self) -> Measurement:
        if not self.connected:
            raise RuntimeError(f"Device '{self.device_id}' is not connected.")

        return await self.generate_measurement()

    @abstractmethod
    async def generate_measurement(self) -> Measurement:
        """
        Generate a simulated measurement.
        """
