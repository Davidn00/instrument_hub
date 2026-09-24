from datetime import UTC

from app.devices.generators import generate_ecg
from app.devices.simulated import SimulatedDevice
from app.models.signal import Signal


class SimulatedECGDevice(SimulatedDevice):
    """
    Simulated ECG acquisition device.
    """

    def __init__(
        self,
        device_id: str,
        sampling_rate: float = 500.0,
        heart_rate: float = 72.0,
        amplitude: float = 1.0,
        noise_amplitude: float = 0.01,
    ) -> None:
        super().__init__(
            device_id=device_id,
            name="Simulated ECG Device",
        )

        self.sampling_rate = sampling_rate
        self.heart_rate = heart_rate
        self.amplitude = amplitude
        self.noise_amplitude = noise_amplitude

    def acquire(
        self,
        duration: float = 10.0,
    ) -> Signal:
        samples = generate_ecg(
            sampling_rate=self.sampling_rate,
            duration=duration,
            heart_rate=self.heart_rate,
            amplitude=self.amplitude,
            noise_amplitude=self.noise_amplitude,
        )

        return Signal(
            samples=samples,
            sampling_rate=self.sampling_rate,
            unit="mV",
            channel="ECG-I",
            metadata={
                "heart_rate": self.heart_rate,
                "device_type": "ECG",
            },
        )

    async def generate_measurement(self):
        signal = self.acquire(duration=1.0 / self.sampling_rate)

        return await self._signal_to_measurement(signal)

    async def _signal_to_measurement(self, signal: Signal):
        from datetime import datetime

        from app.models.measurement import Measurement

        return Measurement(
            timestamp=datetime.now(UTC),
            value=float(signal.samples[0]),
            unit=signal.unit,
            sensor_id=f"{self.device_id}-channel-1",
            device_id=self.device_id,
            measurement_type="ecg",
        )
