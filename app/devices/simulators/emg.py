from datetime import UTC

from app.devices.generators import generate_emg
from app.devices.simulated import SimulatedDevice
from app.models.measurement import Measurement
from app.models.signal import Signal


class SimulatedEMGDevice(SimulatedDevice):
    """
    Simulated EMG acquisition device.
    """

    def __init__(
        self,
        device_id: str,
        sampling_rate: float = 1000.0,
        amplitude: float = 1.0,
        burst_frequency: float = 50.0,
        noise_amplitude: float = 0.05,
    ) -> None:
        super().__init__(
            device_id=device_id,
            name="Simulated EMG Device",
        )

        self.sampling_rate = sampling_rate
        self.amplitude = amplitude
        self.burst_frequency = burst_frequency
        self.noise_amplitude = noise_amplitude

    def acquire(
        self,
        duration: float = 5.0,
    ) -> Signal:
        samples = generate_emg(
            sampling_rate=self.sampling_rate,
            duration=duration,
            amplitude=self.amplitude,
            burst_frequency=self.burst_frequency,
            noise_amplitude=self.noise_amplitude,
        )

        return Signal(
            samples=samples,
            sampling_rate=self.sampling_rate,
            unit="mV",
            channel="EMG-1",
            metadata={
                "device_type": "EMG",
                "burst_frequency": self.burst_frequency,
            },
        )

    async def generate_measurement(self) -> Measurement:
        from datetime import datetime

        from app.models.measurement import Measurement

        signal = self.acquire(duration=1.0 / self.sampling_rate)

        return Measurement(
            timestamp=datetime.now(UTC),
            value=float(signal.samples[0]),
            unit=signal.unit,
            sensor_id=f"{self.device_id}-channel-1",
            device_id=self.device_id,
            measurement_type="emg",
        )
