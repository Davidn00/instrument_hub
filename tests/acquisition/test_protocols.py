import struct

import pytest

from app.acquisition.protocols import (
    ASCIIKeyValueParser,
    BinaryFrameDecoder,
    CSVMeasurementParser,
    Float64BinaryMeasurementParser,
    LineFrameDecoder,
    ProtocolParser,
)


def test_ascii_parser_pipeline() -> None:
    parser = ProtocolParser(
        decoder=LineFrameDecoder(),
        parser=ASCIIKeyValueParser(
            device_id="temp-001",
            default_unit="°C",
            default_measurement_type="temperature",
        ),
    )

    first = parser.feed(b"value=25.1,unit=C")

    assert first == []

    second = parser.feed(b",sensor_id=s1,measurement_type=temperature\r\n")

    assert len(second) == 1
    assert second[0].value == 25.1
    assert second[0].sensor_id == "s1"
    assert second[0].device_id == "temp-001"


def test_csv_parser_supports_partial_reads() -> None:
    parser = ProtocolParser(
        decoder=LineFrameDecoder(protocol="csv"),
        parser=CSVMeasurementParser(device_id="pressure-001"),
    )

    assert parser.feed(b"101.3,kPa,press-1,pressure") == []

    measurements = parser.feed(b",pressure-001\n")

    assert len(measurements) == 1
    assert measurements[0].value == 101.3
    assert measurements[0].unit == "kPa"
    assert measurements[0].measurement_type == "pressure"


def test_binary_parser_supports_fragmented_frame() -> None:
    payload = struct.pack(
        "<d",
        12.5,
    )

    frame = (
        b"\xaa\x55"
        + bytes([1])
        + struct.pack(
            "<H",
            len(payload),
        )
        + payload
    )

    parser = ProtocolParser(
        decoder=BinaryFrameDecoder(),
        parser=Float64BinaryMeasurementParser(
            device_id="binary-001",
            unit="V",
            measurement_type="voltage",
        ),
    )

    assert parser.feed(frame[:3]) == []

    measurements = parser.feed(frame[3:])

    assert len(measurements) == 1
    assert measurements[0].value == pytest.approx(12.5)
    assert measurements[0].unit == "V"


def test_binary_parser_supports_multiple_frames() -> None:
    def make_frame(
        value: float,
    ) -> bytes:
        payload = struct.pack(
            "<d",
            value,
        )

        return b"\xaa\x55" + bytes([1]) + struct.pack("<H", 8) + payload

    parser = ProtocolParser(
        decoder=BinaryFrameDecoder(),
        parser=Float64BinaryMeasurementParser(device_id="binary-002"),
    )

    measurements = parser.feed(make_frame(1.0) + make_frame(2.0))

    assert [item.value for item in measurements] == [1.0, 2.0]


def test_ascii_invalid_value_is_rejected() -> None:
    parser = ProtocolParser(
        decoder=LineFrameDecoder(),
        parser=ASCIIKeyValueParser(device_id="invalid-001"),
    )

    with pytest.raises(
        ValueError,
        match="Invalid measurement value",
    ):
        parser.feed(b"value=not-a-number\n")
