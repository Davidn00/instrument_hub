import struct
from datetime import UTC, datetime

from app.acquisition.protocols.base import (
    Frame,
    FrameDecoder,
    MeasurementParser,
)
from app.models.measurement import Measurement


class BinaryFrameDecoder(FrameDecoder):
    """Decode InstrumentHub binary frames.

    Frame format:

        magic(2)
        +
        version(1)
        +
        payload_length(2, little-endian)
        +
        payload
    """

    HEADER = struct.Struct("<2sBH")

    MAGIC = bytes.fromhex("AA55")

    def __init__(
        self,
        *,
        max_payload_size: int = 4096,
        protocol: str = "binary",
    ) -> None:
        if max_payload_size <= 0:
            raise ValueError("max_payload_size must be greater than zero")

        self.max_payload_size = max_payload_size
        self.protocol = protocol
        self._buffer = bytearray()

    def feed(
        self,
        data: bytes,
    ) -> list[Frame]:
        if data:
            self._buffer.extend(data)

        frames: list[Frame] = []

        while True:
            magic_index = self._buffer.find(self.MAGIC)

            if magic_index < 0:
                if self._buffer[-1:] == self.MAGIC[:1]:
                    self._buffer[:] = self._buffer[-1:]
                else:
                    self._buffer.clear()

                break

            if magic_index:
                del self._buffer[:magic_index]

            if len(self._buffer) < self.HEADER.size:
                break

            _, version, payload_length = self.HEADER.unpack(
                self._buffer[: self.HEADER.size]
            )

            if payload_length > self.max_payload_size:
                raise ValueError("binary payload exceeds max_payload_size")

            total = self.HEADER.size + payload_length

            if len(self._buffer) < total:
                break

            raw = bytes(self._buffer[:total])

            del self._buffer[:total]

            frames.append(
                Frame(
                    raw=raw,
                    received_at=datetime.now(UTC),
                    protocol=self.protocol,
                    metadata={
                        "version": version,
                        "payload_length": payload_length,
                    },
                )
            )

        return frames

    def reset(self) -> None:
        self._buffer.clear()


class Float64BinaryMeasurementParser(MeasurementParser):
    """Parse a binary frame containing one little-endian float64."""

    PAYLOAD_OFFSET = BinaryFrameDecoder.HEADER.size

    def __init__(
        self,
        *,
        device_id: str,
        unit: str = "a.u.",
        measurement_type: str = "measurement",
        sensor_id: str = "sensor-1",
    ) -> None:
        self.device_id = device_id
        self.unit = unit
        self.measurement_type = measurement_type
        self.sensor_id = sensor_id

    def parse(
        self,
        frame: Frame,
    ) -> list[Measurement]:
        payload_length = int(
            frame.metadata.get(
                "payload_length",
                0,
            )
        )

        if payload_length != 8:
            raise ValueError(
                f"Expected an 8-byte float64 payload, got {payload_length} bytes"
            )

        payload = frame.raw[self.PAYLOAD_OFFSET :]

        value = struct.unpack(
            "<d",
            payload,
        )[0]

        return [
            Measurement(
                timestamp=frame.received_at,
                value=value,
                unit=self.unit,
                sensor_id=self.sensor_id,
                device_id=self.device_id,
                measurement_type=self.measurement_type,
                metadata={
                    "protocol": frame.protocol,
                    "frame_version": frame.metadata.get(
                        "version",
                        0,
                    ),
                },
            )
        ]
