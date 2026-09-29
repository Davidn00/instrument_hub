import asyncio
from dataclasses import dataclass
from typing import Any

from app.acquisition.protocols.base import ProtocolParser
from app.devices.base import Instrument
from app.models.measurement import Measurement


@dataclass(slots=True, frozen=True)
class SerialInstrumentConfig:
    """Configuration for a physical serial instrument."""

    port: str
    baudrate: int = 9600
    parity: str = "N"
    stopbits: float = 1.0
    bytesize: int = 8
    timeout: float = 1.0
    write_timeout: float = 1.0
    read_size: int = 4096

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

        if self.read_size <= 0:
            raise ValueError("read_size must be greater than zero")


class SerialInstrument(Instrument):
    """Async-friendly serial instrument backed by PySerial.

    Blocking PySerial calls are executed in worker threads so the event loop
    remains responsive.
    """

    def __init__(
        self,
        *,
        device_id: str,
        name: str,
        config: SerialInstrumentConfig,
        parser: ProtocolParser,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            device_id=device_id,
            name=name,
            metadata=metadata,
        )

        self.config = config
        self.parser = parser

        self._serial: Any = None
        self._pending: list[Measurement] = []

    async def connect(self) -> None:
        if self.connected:
            return

        try:
            import serial
        except ImportError as exc:
            raise RuntimeError(
                "PySerial is required for SerialInstrument. "
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

        self.parser.reset()
        self._pending.clear()

        self._connected = True

    async def disconnect(self) -> None:
        serial_port = self._serial

        self._serial = None
        self._connected = False

        self._pending.clear()
        self.parser.reset()

        if serial_port is not None:
            await asyncio.to_thread(serial_port.close)

    async def read(self) -> Measurement:
        if not self.connected or self._serial is None:
            raise RuntimeError(f"Device '{self.device_id}' is not connected.")

        if self._pending:
            return self._pending.pop(0)

        while True:
            raw = await asyncio.to_thread(
                self._serial.read,
                self.config.read_size,
            )

            if not raw:
                raise TimeoutError(
                    f"Timed out waiting for data from '{self.device_id}'."
                )

            measurements = self.parser.feed(raw)

            if measurements:
                self._pending.extend(measurements[1:])

                return measurements[0]

    async def write(self, data: bytes) -> None:
        if not self.connected or self._serial is None:
            raise RuntimeError(f"Device '{self.device_id}' is not connected.")

        await asyncio.to_thread(
            self._serial.write,
            data,
        )
