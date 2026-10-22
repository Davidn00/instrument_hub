"""Protocol-level hardware simulator for IBSEN I-MON USB spectrometers.

This simulator implements the same asynchronous transport contract used by
IBSENProtocol. It does not open a serial port and is intended for automated
tests, demonstrations, and driver development without physical hardware.
"""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Iterable

import numpy as np


class IBSENHardwareSimulator:
    """Simulate the command/response behavior of an IBSEN spectrometer."""

    CR = b"\r"
    ACK = b"\x06"
    NAK = b"\x15"
    BELL = b"\x07"
    ESC = b"\x1b"

    def __init__(
        self,
        *,
        pixel_count: int = 256,
        serial_number: str = "SIM-IBSEN-001",
        firmware_version: str = "SIM-1.0",
        identification: str = "JETI_MP_SERS",
        peak_pixel: float | None = None,
        peak_intensity: float = 45000.0,
        baseline: float = 500.0,
        noise_std: float = 20.0,
        seed: int = 42,
        nak_commands: Iterable[str] = (),
        malformed_next_spectrum: bool = False,
    ) -> None:
        if pixel_count <= 0:
            raise ValueError("pixel_count must be greater than zero")

        if not 0 <= peak_intensity <= 65535:
            raise ValueError("peak_intensity must be within the 16-bit ADC range")

        if not 0 <= baseline <= 65535:
            raise ValueError("baseline must be within the 16-bit ADC range")

        if noise_std < 0:
            raise ValueError("noise_std cannot be negative")

        self.pixel_count = pixel_count
        self.serial_number = serial_number
        self.firmware_version = firmware_version
        self.identification = identification
        self.peak_pixel = (
            float(pixel_count - 1) / 2 if peak_pixel is None else peak_pixel
        )
        self.peak_intensity = peak_intensity
        self.baseline = baseline
        self.noise_std = noise_std
        self.nak_commands = set(nak_commands)
        self.malformed_next_spectrum = malformed_next_spectrum

        self._rng = np.random.default_rng(seed)
        self._responses: deque[bytes] = deque()
        self._connected = False
        self._format_configured = False
        self._running = False
        self._lock = asyncio.Lock()

        # Useful for assertions in automated tests.
        self.commands_received: list[bytes] = []
        self.spectra_generated = 0

    @property
    def connected(self) -> bool:
        """Return whether the simulated transport is connected."""
        return self._connected

    async def connect(self) -> None:
        """Open the simulated connection."""
        self._connected = True

    async def disconnect(self) -> None:
        """Close the simulated connection and clear pending responses."""
        self._connected = False
        self._running = False
        self._responses.clear()

    async def write(self, data: bytes) -> None:
        """Accept a command and queue its simulated response."""
        if not self._connected:
            raise RuntimeError("IBSEN simulator is not connected")

        if not data:
            raise ValueError("Cannot write an empty command")

        async with self._lock:
            self.commands_received.append(bytes(data))

            # ESC is the stop control byte; it has no text terminator.
            if data == self.ESC:
                self._running = False
                return

            if not data.endswith(self.CR):
                raise ValueError("IBSEN commands must end with CR")

            try:
                command = data[:-1].decode("ascii").strip()
            except UnicodeDecodeError as exc:
                raise ValueError("IBSEN commands must be ASCII") from exc

            if command in self.nak_commands:
                self._responses.append(self.NAK)
                return

            if command == "*IDN?":
                self._queue_line(self.identification)
            elif command == "*PARAmeter:PIXel?":
                self._queue_line(str(self.pixel_count))
            elif command == "*PARAmeter:SERNumber?":
                self._queue_line(self.serial_number)
            elif command == "*VERS?":
                self._queue_line(self.firmware_version)
            elif command.startswith("*CONFigure:FORMat "):
                try:
                    output_format = int(command.rsplit(" ", 1)[1])
                except ValueError:
                    self._responses.append(self.NAK)
                    return

                if output_format != 4:
                    self._responses.append(self.NAK)
                    return

                self._format_configured = True
                self._responses.append(self.ACK)
            elif command == "*INIT":
                self._running = True
                self._responses.append(self.ACK)
            elif command == "*READ 4":
                self._queue_spectrum()
            else:
                # Unknown commands are rejected instead of silently accepted.
                self._responses.append(self.NAK)

    async def read_byte(self) -> bytes:
        """Read one simulated protocol control byte."""
        self._ensure_connected()

        async with self._lock:
            if not self._responses:
                raise TimeoutError("No simulated IBSEN byte is available")

            response = self._responses.popleft()

        if len(response) != 1:
            raise RuntimeError(f"Expected a one-byte response, received {response!r}")

        return response

    async def read_until(
        self,
        delimiter: bytes = b"\r",
        *,
        max_bytes: int = 4096,
    ) -> bytes:
        """Read one queued line, enforcing the requested response limits."""
        self._ensure_connected()

        if not delimiter:
            raise ValueError("delimiter cannot be empty")

        if max_bytes <= 0:
            raise ValueError("max_bytes must be greater than zero")

        async with self._lock:
            if not self._responses:
                raise TimeoutError("No simulated IBSEN line is available")

            response = self._responses.popleft()

        if not response.endswith(delimiter):
            raise ValueError("Simulated response does not end with delimiter")

        if len(response) > max_bytes:
            raise ValueError("Simulated response exceeds max_bytes")

        return response

    def generate_spectrum(self) -> np.ndarray:
        """Generate a reproducible Gaussian-shaped optical spectrum."""
        pixels = np.arange(self.pixel_count, dtype=float)

        # A Gaussian peak provides a realistic, controllable synthetic signal.
        width = max(self.pixel_count / 30.0, 1.0)
        peak = self.peak_intensity * np.exp(
            -0.5 * ((pixels - self.peak_pixel) / width) ** 2
        )

        noise = self._rng.normal(
            loc=0.0,
            scale=self.noise_std,
            size=self.pixel_count,
        )

        intensity = np.clip(
            self.baseline + peak + noise,
            0.0,
            65535.0,
        )

        self.spectra_generated += 1

        return np.rint(intensity).astype(np.uint16)

    def _queue_line(self, value: str) -> None:
        self._responses.append(value.encode("ascii") + self.CR)

    def _queue_spectrum(self) -> None:
        if not self._format_configured:
            self._responses.append(self.NAK)
            return

        self._responses.extend([self.ACK, self.BELL])

        intensities = self.generate_spectrum()

        for index, intensity in enumerate(intensities):
            if self.malformed_next_spectrum and index == 0:
                self._queue_line("INVALID")
            else:
                self._queue_line(str(int(intensity)))

        self.malformed_next_spectrum = False

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("IBSEN simulator is not connected")
