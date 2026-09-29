import asyncio
from collections import deque
from typing import Any

from app.acquisition.protocols.base import ProtocolParser
from app.devices.base import Instrument
from app.models.measurement import Measurement


class TCPInstrument(Instrument):
    """TCP-stream instrument using the same parser pipeline as SerialInstrument."""

    def __init__(
        self,
        *,
        device_id: str,
        name: str,
        host: str,
        port: int,
        parser: ProtocolParser,
        read_size: int = 4096,
        connect_timeout: float = 5.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            device_id=device_id,
            name=name,
            metadata=metadata,
        )

        if not host:
            raise ValueError("host cannot be empty")

        if not 1 <= port <= 65535:
            raise ValueError("port must be between 1 and 65535")

        if read_size <= 0:
            raise ValueError("read_size must be greater than zero")

        if connect_timeout <= 0:
            raise ValueError("connect_timeout must be greater than zero")

        self.host = host
        self.port = port
        self.parser = parser
        self.read_size = read_size
        self.connect_timeout = connect_timeout

        self._reader: asyncio.StreamReader | None = None

        self._writer: asyncio.StreamWriter | None = None

        self._pending: deque[Measurement] = deque()

    async def connect(self) -> None:
        if self.connected:
            return

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(
                self.host,
                self.port,
            ),
            timeout=self.connect_timeout,
        )

        self._reader = reader
        self._writer = writer

        self.parser.reset()
        self._pending.clear()

        self._connected = True

    async def disconnect(self) -> None:
        writer = self._writer

        self._reader = None
        self._writer = None
        self._connected = False

        self._pending.clear()
        self.parser.reset()

        if writer is not None:
            writer.close()
            await writer.wait_closed()

    async def read(self) -> Measurement:
        if not self.connected or self._reader is None:
            raise RuntimeError(f"Device '{self.device_id}' is not connected.")

        if self._pending:
            return self._pending.popleft()

        while True:
            raw = await self._reader.read(self.read_size)

            if not raw:
                raise ConnectionError(f"TCP connection closed by '{self.device_id}'.")

            measurements = self.parser.feed(raw)

            if measurements:
                self._pending.extend(measurements[1:])

                return measurements[0]

    async def write(
        self,
        data: bytes,
    ) -> None:
        if not self.connected or self._writer is None:
            raise RuntimeError(f"Device '{self.device_id}' is not connected.")

        self._writer.write(data)
        await self._writer.drain()
