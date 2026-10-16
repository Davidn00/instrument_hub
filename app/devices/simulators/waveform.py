import math
import time
from datetime import UTC, datetime

from app.devices.simulated import SimulatedDevice
from app.models.measurement import Measurement


class SimulatedSineDevice(SimulatedDevice):
    """Simulated continuous sinusoidal signal source."""

    def __init__(
        self,
        device_id: str,
        frequency: float = 1.0,
        amplitude: float = 1.0,
        sampling_rate: float = 10.0,
    ) -> None:
        super().__init__(
            device_id=device_id,
            name="Simulated Sine Wave Instrument",
        )

        if frequency < 0:
            raise ValueError("frequency cannot be negative")

        if amplitude < 0:
            raise ValueError("amplitude cannot be negative")

        if sampling_rate <= 0:
            raise ValueError("sampling_rate must be greater than zero")

        self.frequency = frequency
        self.amplitude = amplitude
        self.sampling_rate = sampling_rate
        self._started_at = time.monotonic()

    async def connect(self) -> None:
        await super().connect()
        self._started_at = time.monotonic()

    async def generate_measurement(self) -> Measurement:
        elapsed = max(
            0.0,
            time.monotonic() - self._started_at,
        )

        value = self.amplitude * math.sin(2.0 * math.pi * self.frequency * elapsed)

        return Measurement(
            timestamp=datetime.now(UTC),
            value=value,
            unit="V",
            channel=f"{self.device_id}-channel-1",
            device_id=self.device_id,
            measurement_type="voltage",
            metadata={
                "signal_frequency_hz": self.frequency,
                "nominal_sampling_rate_hz": self.sampling_rate,
            },
        )
