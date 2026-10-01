import asyncio
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class SerialTransportConfig:
    """Configuration for an asynchronous facade over PySerial."""

    port: str
    baudrate: int = 921600
    parity: str = "N"
    stopbits: float = 1.0
    bytesize: int = 8
    timeout: float = 1.0
    write_timeout: float = 1.0

    def __post_init__(self) -> None:
        if not self.port:
            raise ValueError("port cannot be empty")

        if self.baudrate <= 0:
            raise ValueError("baudrate must be greater than zero")

        if self.parity.upper() not in {"N", "E", "O", "M", "S"}:
            raise ValueError("parity must be one of N, E, O, M, S")

        if self.stopbits not in {1.0, 1.5, 2.0}:
            raise ValueError("stopbits must be 1.0, 1.5 or 2.0")

        if self.bytesize not in {5, 6, 7, 8}:
            raise ValueError("bytesize must be between 5 and 8")

        if self.timeout < 0:
            raise ValueError("timeout cannot be negative")

        if self.write_timeout < 0:
            raise ValueError("write_timeout cannot be negative")


class SerialTransport:
    """Async-friendly serial byte transport used by physical protocols."""

    def __init__(self, config: SerialTransportConfig) -> None:
        self.config = config
        self._serial: Any = None

    @property
    def connected(self) -> bool:
        return self._serial is not None

    async def connect(self) -> None:
        if self.connected:
            return

        try:
            import serial
        except ImportError as exc:
            raise RuntimeError(
                "PySerial is required for SerialTransport. "
                "Install the 'pyserial' dependency."
            ) from exc

        def open_port() -> Any:
            return serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                parity=self.config.parity.upper(),
                stopbits=self.config.stopbits,
                bytesize=self.config.bytesize,
                timeout=self.config.timeout,
                write_timeout=self.config.write_timeout,
            )

        self._serial = await asyncio.to_thread(open_port)

    async def disconnect(self) -> None:
        serial_port = self._serial
        self._serial = None

        if serial_port is not None:
            await asyncio.to_thread(serial_port.close)

    async def write(self, data: bytes) -> None:
        serial_port = self._require_serial()

        await asyncio.to_thread(
            serial_port.write,
            data,
        )

    async def read_byte(self) -> bytes:
        serial_port = self._require_serial()

        data = await asyncio.to_thread(
            serial_port.read,
            1,
        )

        if not data:
            raise TimeoutError("Timed out waiting for a serial byte.")

        return bytes(data)

    async def read_until(
        self,
        delimiter: bytes = b"\r",
        *,
        max_bytes: int = 4096,
    ) -> bytes:
        if not delimiter:
            raise ValueError("delimiter cannot be empty")

        if max_bytes <= 0:
            raise ValueError("max_bytes must be greater than zero")

        serial_port = self._require_serial()

        def read_line() -> bytes:
            data = serial_port.read_until(
                delimiter,
                max_bytes,
            )

            if not data:
                raise TimeoutError("Timed out waiting for serial data.")

            if not data.endswith(delimiter):
                raise ValueError(
                    "Serial response exceeded max_bytes or was incomplete."
                )

            return bytes(data)

        return await asyncio.to_thread(read_line)

    def _require_serial(self) -> Any:
        if self._serial is None:
            raise RuntimeError("Serial transport is not connected.")

        return self._serial
