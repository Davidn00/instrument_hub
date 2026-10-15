from collections import OrderedDict
from datetime import UTC, datetime

from app.devices.generators import generate_fbg_spectrum
from app.devices.simulated import SimulatedDevice
from app.models.measurement import Measurement
from app.models.signal import Signal
from app.models.spectrum import Spectrum


class SimulatedFBGDevice(SimulatedDevice):
    """Simulated Fiber Bragg Grating interrogator."""

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

        if points <= 1:
            raise ValueError("points must be greater than one")

        if wavelength_start >= wavelength_end:
            raise ValueError("wavelength_start must be lower than wavelength_end")

        self.center_wavelength = center_wavelength
        self.wavelength_start = wavelength_start
        self.wavelength_end = wavelength_end
        self.points = points
        self.noise_amplitude = noise_amplitude

        self.last_spectrum: Spectrum | None = None

        # Relaciona cada lectura con su espectro exacto.
        # El límite evita acumular espectros indefinidamente si
        # el consumidor de adquisición se retrasa.
        self._spectra_by_timestamp: OrderedDict[datetime, Spectrum] = OrderedDict()

    def _generate_spectrum(
        self,
        *,
        associate_with_measurement: bool,
    ) -> Spectrum:
        wavelengths, intensities = generate_fbg_spectrum(
            center_wavelength=self.center_wavelength,
            wavelength_start=self.wavelength_start,
            wavelength_end=self.wavelength_end,
            points=self.points,
            noise_amplitude=self.noise_amplitude,
        )

        timestamp = datetime.now(UTC)

        spectrum = Spectrum(
            timestamp=timestamp,
            device_id=self.device_id,
            wavelength=wavelengths,
            intensity=intensities,
            wavelength_unit="nm",
            intensity_unit="a.u.",
            metadata={
                "instrument_type": "simulated_fbg",
                "center_wavelength_nm": self.center_wavelength,
                "wavelength_start_nm": self.wavelength_start,
                "wavelength_end_nm": self.wavelength_end,
                "number_of_pixels": self.points,
            },
        )

        self.last_spectrum = spectrum

        if associate_with_measurement:
            self._spectra_by_timestamp[timestamp] = spectrum

            while len(self._spectra_by_timestamp) > 2048:
                self._spectra_by_timestamp.popitem(last=False)

        return spectrum

    def get_spectrum_for_measurement(
        self,
        timestamp: datetime,
    ) -> Spectrum | None:
        """Return the spectrum corresponding to a measurement."""
        return self._spectra_by_timestamp.pop(timestamp, None)

    def acquire(self) -> Signal:
        """Acquire an optical signal for the existing signal interface."""
        spectrum = self._generate_spectrum(
            associate_with_measurement=False,
        )

        return Signal(
            samples=spectrum.intensity,
            sampling_rate=1.0,
            unit="a.u.",
            channel="FBG-1",
            metadata={
                **spectrum.metadata,
                "wavelength_axis": spectrum.wavelength.tolist(),
            },
        )

    async def generate_measurement(self) -> Measurement:
        """Generate one measurement and its associated optical spectrum."""
        spectrum = self._generate_spectrum(
            associate_with_measurement=True,
        )

        return Measurement(
            timestamp=spectrum.timestamp,
            value=spectrum.peak_wavelength,
            unit="nm",
            channel="FBG-1",
            device_id=self.device_id,
            quality="GOOD",
            metadata={
                "measurement_type": "fbg_peak_wavelength",
                "spectrum_points": spectrum.number_of_pixels,
                "peak_intensity": spectrum.peak_intensity,
            },
        )
