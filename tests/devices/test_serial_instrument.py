import sys
import types

import pytest

from app.acquisition.protocols import (
    ASCIIKeyValueParser,
    LineFrameDecoder,
    ProtocolParser,
)
from app.devices.instruments.serial import (
    SerialInstrument,
    SerialInstrumentConfig,
)


class FakeSerialPort:
    def __init__(
        self,
        **kwargs: object,
    ) -> None:
        self.kwargs = kwargs
        self.closed = False

        self.chunks = [
            (b"value=25.4,unit=C,measurement_type=temperature\n"),
        ]

    def read(
        self,
        size: int,
    ) -> bytes:
        if self.chunks:
            return self.chunks.pop(0)

        return b""

    def write(
        self,
        data: bytes,
    ) -> int:
        return len(data)

    def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_serial_instrument_uses_pyserial(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_serial_module = types.SimpleNamespace(
        Serial=FakeSerialPort,
    )

    monkeypatch.setitem(
        sys.modules,
        "serial",
        fake_serial_module,
    )

    parser = ProtocolParser(
        decoder=LineFrameDecoder(),
        parser=ASCIIKeyValueParser(
            device_id="serial-001",
            default_unit="°C",
            default_measurement_type="temperature",
        ),
    )

    instrument = SerialInstrument(
        device_id="serial-001",
        name="Test Serial Instrument",
        config=SerialInstrumentConfig(
            port="COM3",
            baudrate=115200,
            parity="N",
            stopbits=1.0,
            timeout=0.1,
        ),
        parser=parser,
    )

    await instrument.connect()

    measurement = await instrument.read()

    await instrument.disconnect()

    assert measurement.value == 25.4
    assert measurement.unit == "C"
    assert instrument.connected is False


def test_serial_config_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        SerialInstrumentConfig(
            port="COM1",
            baudrate=0,
        )

    with pytest.raises(ValueError):
        SerialInstrumentConfig(
            port="COM1",
            parity="X",
        )

    with pytest.raises(ValueError):
        SerialInstrumentConfig(
            port="COM1",
            stopbits=3.0,
        )
