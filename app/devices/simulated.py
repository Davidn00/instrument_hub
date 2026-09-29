from abc import abstractmethod

from app.devices.base import Instrument
from app.models.measurement import Measurement


class SimulatedInstrument(Instrument):
    """Base class for virtual instruments."""

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
        """Generate one simulated measurement."""


# Backward-compatible Stage 2 name.
SimulatedDevice = SimulatedInstrument
