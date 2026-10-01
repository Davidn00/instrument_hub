from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

import numpy as np

from app.models.spectrum import Spectrum


class IBSENTransport(Protocol):
    async def write(self, data: bytes) -> None: ...

    async def read_byte(self) -> bytes: ...

    async def read_until(
        self,
        delimiter: bytes = b"\r",
        *,
        max_bytes: int = 4096,
    ) -> bytes: ...


class IBSENProtocolError(RuntimeError):
    """Base error for the I-MON USB protocol."""


class IBSENCommandError(IBSENProtocolError):
    """The instrument returned NAK or an invalid control response."""


@dataclass(slots=True, frozen=True)
class IBSENDeviceInfo:
    identification: str
    pixel_count: int
    serial_number: str | None = None
    firmware_version: str | None = None


@dataclass(slots=True, frozen=True)
class IBSENCalibration:
    """Per-unit wavelength calibration coefficients.

    λ(p) = A + B1*p + B2*p² + B3*p³ + B4*p⁴ + B5*p⁵
    """

    a: float
    b1: float
    b2: float
    b3: float
    b4: float
    b5: float

    def wavelength(self, pixel: float) -> float:
        return (
            self.a
            + self.b1 * pixel
            + self.b2 * pixel**2
            + self.b3 * pixel**3
            + self.b4 * pixel**4
            + self.b5 * pixel**5
        )

    def wavelengths(
        self,
        pixel_count: int,
    ) -> list[float]:
        if pixel_count <= 0:
            raise ValueError("pixel_count must be greater than zero")

        return [self.wavelength(float(pixel)) for pixel in range(pixel_count)]

    @classmethod
    def from_user_block(
        cls,
        block: bytes,
    ) -> IBSENCalibration:
        """Parse the documented wavelength-calibration block.

        The supplied manufacturer documentation defines the six
        16-byte ASCII coefficient fields. The checksum algorithm
        is intentionally not implemented here because it is not
        specified sufficiently in the supplied documentation.
        """

        if len(block) < 96:
            raise ValueError("IBSEN wavelength calibration block is too short")

        values: list[float] = []

        for offset in range(0, 96, 16):
            field = block[offset : offset + 16].split(b"\x00", 1)[0].strip()

            try:
                values.append(float(field.decode("ascii")))
            except (
                UnicodeDecodeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    f"Invalid IBSEN calibration coefficient at offset {offset}"
                ) from exc

        return cls(*values)


class IBSENProtocol:
    """Protocol implementation for I-MON USB VCP."""

    CR = b"\r"

    ACK = b"\x06"
    NAK = b"\x15"
    BELL = b"\x07"
    ESC = b"\x1b"

    FORMAT_ASCII_CR = 4

    MAX_ASCII_LINE = 128
    MAX_INTENSITY = 65535

    def __init__(
        self,
        transport: IBSENTransport,
        *,
        pixel_count: int | None = None,
    ) -> None:
        self.transport = transport
        self.pixel_count = pixel_count
        self.device_info: IBSENDeviceInfo | None = None

    async def initialize(self) -> IBSENDeviceInfo:
        identification = await self.query("*IDN?")

        pixel_count = int(await self.query("*PARAmeter:PIXel?"))

        if pixel_count <= 0:
            raise IBSENProtocolError(f"Invalid IBSEN pixel count: {pixel_count}")

        serial_number = await self._optional_query("*PARAmeter:SERNumber?")

        firmware_version = await self._optional_query("*VERS?")

        if self.pixel_count is not None and self.pixel_count != pixel_count:
            raise IBSENProtocolError(
                f"Configured pixel_count={self.pixel_count} "
                "does not match "
                f"instrument pixel_count={pixel_count}"
            )

        self.pixel_count = pixel_count

        self.device_info = IBSENDeviceInfo(
            identification=identification,
            pixel_count=pixel_count,
            serial_number=serial_number,
            firmware_version=firmware_version,
        )

        await self.execute(f"*CONFigure:FORMat {self.FORMAT_ASCII_CR}")

        return self.device_info

    async def execute(
        self,
        command: str,
    ) -> None:
        await self._send(command)

        response = await self.transport.read_byte()

        if response == self.NAK:
            raise IBSENCommandError(f"IBSEN command rejected: {command}")

        if response != self.ACK:
            raise IBSENCommandError(
                f"Unexpected IBSEN command response {response!r} for {command}"
            )

    async def query(
        self,
        command: str,
    ) -> str:
        await self._send(command)

        response = await self.transport.read_until(
            self.CR,
            max_bytes=self.MAX_ASCII_LINE,
        )

        return self._clean_text_response(
            response,
            command,
        )

    async def read_spectrum(self) -> Spectrum:
        if self.pixel_count is None:
            raise IBSENProtocolError("IBSEN protocol is not initialized")

        await self._send(f"*READ {self.FORMAT_ASCII_CR}")

        ack = await self.transport.read_byte()

        if ack == self.NAK:
            raise IBSENCommandError("IBSEN rejected *READ")

        if ack != self.ACK:
            raise IBSENCommandError(f"Unexpected IBSEN *READ response: {ack!r}")

        bell = await self.transport.read_byte()

        if bell != self.BELL:
            raise IBSENCommandError(
                f"Expected IBSEN measurement-complete BELL, got {bell!r}"
            )

        intensities: list[float] = []

        for _ in range(self.pixel_count):
            raw = await self.transport.read_until(
                self.CR,
                max_bytes=self.MAX_ASCII_LINE,
            )

            value_text = raw.rstrip(self.CR).strip().decode("ascii")

            try:
                value = float(value_text)
            except ValueError as exc:
                raise IBSENProtocolError(
                    f"Invalid IBSEN intensity value: {value_text!r}"
                ) from exc

            if not 0 <= value <= self.MAX_INTENSITY:
                raise IBSENProtocolError(
                    f"IBSEN intensity outside 16-bit ADC range: {value}"
                )

            intensities.append(value)

        timestamp = datetime.now(UTC)

        return Spectrum(
            timestamp=timestamp,
            device_id=(
                self.device_info.serial_number
                if self.device_info and self.device_info.serial_number
                else "ibsen"
            ),
            wavelength=np.asarray(
                [float(pixel) for pixel in range(self.pixel_count)],
                dtype=float,
            ),
            intensity=np.asarray(
                intensities,
                dtype=float,
            ),
            wavelength_unit="pixel",
            metadata={
                "raw_pixel_count": self.pixel_count,
            },
        )

    async def stop(self) -> None:
        await self._send_control(self.ESC)

    async def _send(
        self,
        command: str,
    ) -> None:
        if not command or "\r" in command or "\n" in command:
            raise ValueError("IBSEN command must be a non-empty single line")

        await self.transport.write(command.encode("ascii") + self.CR)

    async def _send_control(
        self,
        data: bytes,
    ) -> None:
        await self.transport.write(data)

    async def _optional_query(
        self,
        command: str,
    ) -> str | None:
        try:
            value = await self.query(command)
        except (
            IBSENProtocolError,
            TimeoutError,
        ):
            return None

        return value or None

    @classmethod
    def _clean_text_response(
        cls,
        response: bytes,
        command: str,
    ) -> str:
        payload = response.rstrip(cls.CR)

        if payload.startswith(cls.NAK):
            raise IBSENCommandError(f"IBSEN query rejected: {command}")

        if payload.startswith(cls.ACK):
            payload = payload[1:]

        try:
            return payload.decode("ascii").strip()
        except UnicodeDecodeError as exc:
            raise IBSENProtocolError(
                f"Non-ASCII response from IBSEN for {command}"
            ) from exc
