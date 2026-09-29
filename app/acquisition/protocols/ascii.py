from datetime import UTC, datetime

from app.acquisition.protocols.base import (
    Frame,
    FrameDecoder,
    MeasurementParser,
)
from app.models.measurement import Measurement


class LineFrameDecoder(FrameDecoder):
    """Decode newline-delimited ASCII/CSV-like frames."""

    def __init__(
        self,
        *,
        delimiter: bytes = b"\n",
        max_frame_size: int = 4096,
        protocol: str = "ascii",
    ) -> None:
        if not delimiter:
            raise ValueError("delimiter cannot be empty")

        if max_frame_size <= 0:
            raise ValueError("max_frame_size must be greater than zero")

        self.delimiter = delimiter
        self.max_frame_size = max_frame_size
        self.protocol = protocol
        self._buffer = bytearray()

    def feed(
        self,
        data: bytes,
    ) -> list[Frame]:
        if data:
            self._buffer.extend(data)

        frames: list[Frame] = []

        while self.delimiter in self._buffer:
            index = self._buffer.index(self.delimiter)

            raw = bytes(self._buffer[:index])

            del self._buffer[: index + len(self.delimiter)]

            raw = raw.rstrip(b"\r")

            if not raw:
                continue

            if len(raw) > self.max_frame_size:
                raise ValueError("ASCII frame exceeds max_frame_size")

            frames.append(
                Frame(
                    raw=raw,
                    received_at=datetime.now(UTC),
                    protocol=self.protocol,
                )
            )

        if len(self._buffer) > self.max_frame_size:
            raise ValueError("ASCII frame exceeds max_frame_size")

        return frames

    def reset(self) -> None:
        self._buffer.clear()


class ASCIIKeyValueParser(MeasurementParser):
    """Parse value=25.1,unit=C,sensor_id=s1,... frames."""

    def __init__(
        self,
        *,
        device_id: str,
        default_unit: str = "a.u.",
        default_measurement_type: str = "measurement",
        default_sensor_id: str = "sensor-1",
    ) -> None:
        self.device_id = device_id
        self.default_unit = default_unit
        self.default_measurement_type = default_measurement_type
        self.default_sensor_id = default_sensor_id

    def parse(
        self,
        frame: Frame,
    ) -> list[Measurement]:
        text = frame.raw.decode(
            "ascii",
            errors="strict",
        ).strip()

        fields: dict[str, str] = {}

        for item in text.split(","):
            if "=" not in item:
                continue

            key, field_value = item.split(
                "=",
                1,
            )

            fields[key.strip()] = field_value.strip()

        if "value" not in fields:
            raise ValueError(f"ASCII frame has no value field: {text!r}")

        try:
            value = float(fields["value"])
        except ValueError as exc:
            raise ValueError(f"Invalid measurement value: {fields['value']!r}") from exc

        return [
            Measurement(
                timestamp=frame.received_at,
                value=value,
                unit=fields.get(
                    "unit",
                    self.default_unit,
                ),
                sensor_id=fields.get(
                    "sensor_id",
                    self.default_sensor_id,
                ),
                device_id=fields.get(
                    "device_id",
                    self.device_id,
                ),
                measurement_type=fields.get(
                    "measurement_type",
                    self.default_measurement_type,
                ),
                metadata={
                    "protocol": frame.protocol,
                },
            )
        ]


class CSVMeasurementParser(MeasurementParser):
    """Parse value,unit,sensor_id,measurement_type[,device_id]."""

    def __init__(
        self,
        *,
        device_id: str,
        default_unit: str = "a.u.",
        default_measurement_type: str = "measurement",
        default_sensor_id: str = "sensor-1",
    ) -> None:
        self.device_id = device_id
        self.default_unit = default_unit
        self.default_measurement_type = default_measurement_type
        self.default_sensor_id = default_sensor_id

    def parse(
        self,
        frame: Frame,
    ) -> list[Measurement]:
        parts = [part.strip() for part in frame.raw.decode("ascii").split(",")]

        if not parts or not parts[0]:
            raise ValueError("CSV frame has no value")

        try:
            value = float(parts[0])
        except ValueError as exc:
            raise ValueError(f"Invalid CSV measurement value: {parts[0]!r}") from exc

        return [
            Measurement(
                timestamp=frame.received_at,
                value=value,
                unit=(parts[1] if len(parts) > 1 and parts[1] else self.default_unit),
                sensor_id=(
                    parts[2] if len(parts) > 2 and parts[2] else self.default_sensor_id
                ),
                measurement_type=(
                    parts[3]
                    if len(parts) > 3 and parts[3]
                    else self.default_measurement_type
                ),
                device_id=(parts[4] if len(parts) > 4 and parts[4] else self.device_id),
                metadata={
                    "protocol": frame.protocol,
                },
            )
        ]
