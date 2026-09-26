from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np

from app.devices.base import InstrumentDevice
from app.devices.generators import (
    generate_ecg,
    generate_emg,
    generate_fbg_spectrum,
    generate_noise,
    generate_sine,
)
from app.devices.simulators import (
    SimulatedECGDevice,
    SimulatedEMGDevice,
    SimulatedFBGDevice,
    SimulatedPressureDevice,
    SimulatedSineDevice,
    SimulatedTemperatureDevice,
)
from app.models.measurement import Measurement
from app.models.signal import Signal


@dataclass(slots=True)
class GeneratedSignal:
    signal_type: str
    samples: np.ndarray
    sampling_rate: float
    unit: str
    metadata: dict[str, Any]


class UnknownSimulationDeviceError(ValueError):
    """Raised when an unknown simulated device is requested."""


class UnsupportedAcquisitionError(ValueError):
    """Raised when a device cannot perform waveform acquisition."""


class DeviceFactory(Protocol):
    def __call__(
        self,
        *,
        device_id: str,
    ) -> InstrumentDevice: ...


class SimulationService:
    """
    Application service for InstrumentHub simulation.
    This layer intentionally contains no FastAPI dependencies.
    """

    _device_factories: dict[str, DeviceFactory] = {
        "temperature": SimulatedTemperatureDevice,
        "pressure": SimulatedPressureDevice,
        "sine": SimulatedSineDevice,
        "ecg": SimulatedECGDevice,
        "emg": SimulatedEMGDevice,
        "fbg": SimulatedFBGDevice,
    }

    _device_descriptions: dict[str, str] = {
        "temperature": ("Virtual temperature sensor with configurable noise."),
        "pressure": ("Virtual pressure sensor with configurable noise."),
        "sine": ("Virtual sinusoidal waveform instrument."),
        "ecg": ("Synthetic ECG acquisition device."),
        "emg": ("Synthetic EMG acquisition device."),
        "fbg": ("Synthetic Fiber Bragg Grating interrogator."),
    }

    def list_devices(self) -> list[dict[str, str]]:
        return [
            {
                "device_type": device_type,
                "name": type(factory).__name__,
                "description": self._device_descriptions[device_type],
            }
            for device_type, factory in self._device_factories.items()
        ]

    def _create_device(
        self,
        device_type: str,
        device_id: str,
    ) -> InstrumentDevice:
        factory = self._device_factories.get(device_type)

        if factory is None:
            raise UnknownSimulationDeviceError(
                f"Unknown simulated device: {device_type}"
            )

        return factory(device_id=device_id)

    async def read_measurement(
        self,
        device_type: str,
        device_id: str,
    ) -> Measurement:
        device = self._create_device(
            device_type=device_type,
            device_id=device_id,
        )

        await device.connect()

        try:
            return await device.read()
        finally:
            await device.disconnect()

    def acquire_signal(
        self,
        device_type: str,
        device_id: str,
        duration: float,
    ) -> Signal:
        if device_type == "ecg":
            ecg_device = SimulatedECGDevice(device_id=device_id)

            return ecg_device.acquire(duration=duration)

        if device_type == "emg":
            emg_device = SimulatedEMGDevice(device_id=device_id)

            return emg_device.acquire(duration=duration)

        if device_type == "fbg":
            fbg_device = SimulatedFBGDevice(device_id=device_id)

            return fbg_device.acquire()

        if device_type == "sine":
            sine_device = SimulatedSineDevice(device_id=device_id)

            samples = generate_sine(
                frequency=sine_device.frequency,
                amplitude=sine_device.amplitude,
                sampling_rate=sine_device.sampling_rate,
                duration=duration,
            )

            return Signal(
                samples=samples,
                sampling_rate=sine_device.sampling_rate,
                unit="V",
                channel="channel-1",
                metadata={
                    "device_type": "sine",
                    "frequency": sine_device.frequency,
                },
            )

        raise UnsupportedAcquisitionError(
            f"Device '{device_type}' does not support signal acquisition."
        )

    def generate_signal(
        self,
        signal_type: str,
        parameters: dict[str, Any],
    ) -> GeneratedSignal:
        if signal_type == "sine":
            samples = generate_sine(**parameters)

            return GeneratedSignal(
                signal_type="sine",
                samples=samples,
                sampling_rate=float(parameters["sampling_rate"]),
                unit="V",
                metadata={},
            )

        if signal_type == "noise":
            samples = generate_noise(**parameters)

            return GeneratedSignal(
                signal_type="noise",
                samples=samples,
                sampling_rate=float(parameters["sampling_rate"]),
                unit="V",
                metadata={},
            )

        if signal_type == "ecg":
            samples = generate_ecg(**parameters)

            return GeneratedSignal(
                signal_type="ecg",
                samples=samples,
                sampling_rate=float(parameters["sampling_rate"]),
                unit="mV",
                metadata={
                    "heart_rate": parameters["heart_rate"],
                },
            )

        if signal_type == "emg":
            samples = generate_emg(**parameters)

            return GeneratedSignal(
                signal_type="emg",
                samples=samples,
                sampling_rate=float(parameters["sampling_rate"]),
                unit="mV",
                metadata={
                    "burst_frequency": parameters["burst_frequency"],
                },
            )

        if signal_type == "fbg_spectrum":
            wavelengths, samples = generate_fbg_spectrum(**parameters)

            return GeneratedSignal(
                signal_type="fbg_spectrum",
                samples=samples,
                sampling_rate=1.0,
                unit="a.u.",
                metadata={
                    "wavelengths_nm": wavelengths.tolist(),
                    "center_wavelength_nm": parameters["center_wavelength"],
                },
            )

        raise ValueError(f"Unsupported signal type: {signal_type}")
