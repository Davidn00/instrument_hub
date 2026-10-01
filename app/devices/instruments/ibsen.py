from __future__ import annotations

from typing import Any

import numpy as np

from app.acquisition.protocols.ibsen import (
    IBSENCalibration,
    IBSENProtocol,
    IBSENTransport,
)
from app.acquisition.transports.serial import (
    SerialTransport,
    SerialTransportConfig,
)
from app.devices.base import Instrument
from app.models.measurement import Measurement
from app.models.spectrum import Spectrum


class IBSENInstrument(Instrument):
    """Driver for Ibsen Photonics I-MON USB spectrometers."""

    def __init__(
        self,
        *,
        device_id: str,
        name: str,
        transport: IBSENTransport,
        calibration: IBSENCalibration,
        metadata: dict[str, Any] | None = None,
        expected_pixel_count: int | None = None,
    ) -> None:
        super().__init__(
            device_id=device_id,
            name=name,
            metadata=metadata,
        )

        self.transport = transport
        self.calibration = calibration
        self.expected_pixel_count = expected_pixel_count

        self.protocol = IBSENProtocol(
            transport,
            pixel_count=expected_pixel_count,
        )

        self._last_spectrum: Spectrum | None = None

    @classmethod
    def from_serial(
        cls,
        *,
        device_id: str,
        name: str,
        port: str,
        calibration: IBSENCalibration,
        baudrate: int = 921600,
        metadata: dict[str, Any] | None = None,
        expected_pixel_count: int | None = None,
    ) -> IBSENInstrument:
        if baudrate not in {
            38400,
            115200,
            921600,
        }:
            raise ValueError("IBSEN baudrate must be one of 38400, 115200 or 921600")

        transport = SerialTransport(
            SerialTransportConfig(
                port=port,
                baudrate=baudrate,
                parity="N",
                stopbits=1.0,
                bytesize=8,
            )
        )

        return cls(
            device_id=device_id,
            name=name,
            transport=transport,
            calibration=calibration,
            metadata=metadata,
            expected_pixel_count=expected_pixel_count,
        )

    async def connect(self) -> None:
        if self.connected:
            return

        connect = getattr(
            self.transport,
            "connect",
            None,
        )

        if connect is None:
            raise RuntimeError("IBSEN transport does not provide connect()")

        await connect()

        try:
            await self.protocol.initialize()
        except Exception:
            disconnect = getattr(
                self.transport,
                "disconnect",
                None,
            )

            if disconnect is not None:
                await disconnect()

            raise

        self._connected = True

    async def disconnect(self) -> None:
        self._last_spectrum = None
        self._connected = False

        disconnect = getattr(
            self.transport,
            "disconnect",
            None,
        )

        if disconnect is not None:
            await disconnect()

    async def start(self) -> None:
        if not self.connected:
            await self.connect()

        await self.protocol.execute("*INIT")

    async def stop(self) -> None:
        if self.connected:
            await self.protocol.stop()

    async def read_spectrum(self) -> Spectrum:
        if not self.connected:
            raise RuntimeError(f"Device '{self.device_id}' is not connected.")

        raw_spectrum = await self.protocol.read_spectrum()

        pixels = range(raw_spectrum.number_of_pixels)

        wavelengths = [self.calibration.wavelength(float(pixel)) for pixel in pixels]

        spectrum = Spectrum(
            timestamp=raw_spectrum.timestamp,
            device_id=self.device_id,
            wavelength=np.asarray(
                wavelengths,
                dtype=float,
            ),
            intensity=raw_spectrum.intensity,
            metadata={
                **raw_spectrum.metadata,
                "instrument": "I-MON USB",
                "calibration": ("5th-degree-polynomial"),
            },
        )

        self._last_spectrum = spectrum

        return spectrum

    async def read_measurement(
        self,
    ) -> Measurement:
        spectrum = await self.read_spectrum()

        return Measurement(
            timestamp=spectrum.timestamp,
            device_id=self.device_id,
            channel="optical_spectrum_peak",
            value=spectrum.peak_intensity,
            unit="counts",
            quality="GOOD",
            metadata={
                "measurement_type": ("optical_spectrum_peak"),
                "peak_wavelength_nm": (spectrum.peak_wavelength),
                "pixel_count": (spectrum.number_of_pixels),
                "wavelength_nm": (spectrum.wavelength.tolist()),
                "intensity_counts": (spectrum.intensity.tolist()),
            },
        )

    async def read(self) -> Measurement:
        return await self.read_measurement()

    @property
    def last_spectrum(self) -> Spectrum | None:
        return self._last_spectrum
