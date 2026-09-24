from datetime import UTC, datetime

from app.devices.generators import generate_sine
from app.devices.simulated import SimulatedDevice
from app.models.measurement import Measurement


class SimulatedSineDevice(SimulatedDevice):
    """
    Simulated waveform instrument.
    """

    def __init__(
        self,
        device_id: str,
        frequency: float = 10.0,
        amplitude: float = 1.0,
        sampling_rate: float = 1000.0,
    ) -> None:
        super().__init__(
            device_id=device_id,
            name="Simulated Sine Wave Instrument",
        )

        self.frequency = frequency
        self.amplitude = amplitude
        self.sampling_rate = sampling_rate

    async def generate_measurement(self) -> Measurement:
        samples = generate_sine(
            frequency=self.frequency,
            amplitude=self.amplitude,
            sampling_rate=self.sampling_rate,
            duration=1.0 / self.sampling_rate,
        )

        return Measurement(
            timestamp=datetime.now(UTC),
            value=float(samples[0]),
            unit="V",
            sensor_id=f"{self.device_id}-channel-1",
            device_id=self.device_id,
            measurement_type="voltage",
            metadata={
                "frequency": self.frequency,
                "sampling_rate": self.sampling_rate,
            },
        )
