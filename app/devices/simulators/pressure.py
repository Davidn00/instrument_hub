from datetime import UTC, datetime

import numpy as np

from app.devices.simulated import SimulatedDevice
from app.models.measurement import Measurement


class SimulatedPressureDevice(SimulatedDevice):
    """
    Simulated pressure sensor.
    """

    def __init__(
        self,
        device_id: str,
        base_pressure: float = 101.325,
        noise: float = 0.05,
    ) -> None:
        super().__init__(
            device_id=device_id,
            name="Simulated Pressure Sensor",
        )

        self.base_pressure = base_pressure
        self.noise = noise

    async def generate_measurement(self) -> Measurement:
        value = float(self.base_pressure + np.random.normal(0.0, self.noise))

        return Measurement(
            timestamp=datetime.now(UTC),
            value=value,
            unit="kPa",
            sensor_id=f"{self.device_id}-sensor",
            device_id=self.device_id,
            measurement_type="pressure",
        )
