from datetime import UTC, datetime

import numpy as np

from app.devices.simulated import SimulatedDevice
from app.models.measurement import Measurement


class SimulatedTemperatureDevice(SimulatedDevice):
    """
    Simulated temperature sensor.
    """

    def __init__(
        self,
        device_id: str,
        base_temperature: float = 25.0,
        noise: float = 0.1,
    ) -> None:
        super().__init__(
            device_id=device_id,
            name="Simulated Temperature Sensor",
        )

        self.base_temperature = base_temperature
        self.noise = noise

    async def generate_measurement(self) -> Measurement:
        value = float(self.base_temperature + np.random.normal(0.0, self.noise))

        return Measurement(
            timestamp=datetime.now(UTC),
            value=value,
            unit="°C",
            sensor_id=f"{self.device_id}-sensor",
            device_id=self.device_id,
            measurement_type="temperature",
        )
