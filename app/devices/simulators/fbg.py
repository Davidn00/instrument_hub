from datetime import UTC

from app.devices.generators import generate_fbg_spectrum
from app.devices.simulated import SimulatedDevice
from app.models.signal import Signal


class SimulatedFBGDevice(SimulatedDevice):
    """
    Simulated Fiber Bragg Grating interrogator.
    """

    def __init__(
        self,
        device_id: str,
        center_wavelength: float = 1550.23,
        wavelength_start: float = 1548.0,
        wavelength_end: float = 1552.0,
        points: int = 2000,
        noise_amplitude: float = 0.01,
    ) -> None:
        super().__init__(
            device_id=device_id,
            name="Simulated FBG Interrogator",
        )

        self.center_wavelength = center_wavelength
        self.wavelength_start = wavelength_start
        self.wavelength_end = wavelength_end
        self.points = points
        self.noise_amplitude = noise_amplitude

    def acquire(
        self,
    ) -> Signal:
        wavelengths, spectrum = generate_fbg_spectrum(
            center_wavelength=self.center_wavelength,
            wavelength_start=self.wavelength_start,
            wavelength_end=self.wavelength_end,
            points=self.points,
            noise_amplitude=self.noise_amplitude,
        )

        return Signal(
            samples=spectrum,
            sampling_rate=1.0,
            unit="a.u.",
            channel="FBG-1",
            metadata={
                "device_type": "FBG",
                "wavelength_start_nm": self.wavelength_start,
                "wavelength_end_nm": self.wavelength_end,
                "center_wavelength_nm": self.center_wavelength,
                "wavelength_axis": wavelengths.tolist(),
            },
        )

    async def generate_measurement(self):
        from datetime import datetime

        from app.models.measurement import Measurement

        return Measurement(
            timestamp=datetime.now(UTC),
            value=self.center_wavelength,
            unit="nm",
            sensor_id=f"{self.device_id}-sensor-1",
            device_id=self.device_id,
            measurement_type="fbg_wavelength",
            metadata={
                "spectrum_points": self.points,
            },
        )
