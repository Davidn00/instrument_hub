from collections import deque

import pytest

from app.acquisition.protocols.ibsen import (
    IBSENCalibration,
)
from app.devices.instruments.ibsen import (
    IBSENInstrument,
)


class FakeIBSENTransport:
    def __init__(self) -> None:
        self.responses = deque(
            [
                b"JETI_MP_SERS\r",
                b"3\r",
                b"SN123\r",
                b"FW1.2\r",
                b"\x06",
            ]
        )

        self.connected = False
        self.writes: list[bytes] = []

    async def connect(self) -> None:
        self.connected = True

    async def disconnect(self) -> None:
        self.connected = False

    async def write(
        self,
        data: bytes,
    ) -> None:
        self.writes.append(data)

        if data == b"*READ 4\r":
            self.responses.extend(
                [
                    b"\x06",
                    b"\x07",
                    b"100\r",
                    b"200\r",
                    b"300\r",
                ]
            )

    async def read_byte(self) -> bytes:
        return self.responses.popleft()

    async def read_until(
        self,
        delimiter: bytes = b"\r",
        *,
        max_bytes: int = 4096,
    ) -> bytes:
        return self.responses.popleft()


@pytest.mark.asyncio
async def test_ibsen_instrument_connects_and_calibrates_spectrum() -> None:
    transport = FakeIBSENTransport()

    instrument = IBSENInstrument(
        device_id="ibsen-001",
        name="I-MON USB",
        transport=transport,
        expected_pixel_count=3,
        calibration=IBSENCalibration(
            a=1500.0,
            b1=1.0,
            b2=0.0,
            b3=0.0,
            b4=0.0,
            b5=0.0,
        ),
    )

    await instrument.connect()

    spectrum = await instrument.read_spectrum()

    measurement = await instrument.read_measurement()

    await instrument.disconnect()

    assert spectrum.wavelength.tolist() == [
        1500.0,
        1501.0,
        1502.0,
    ]

    assert spectrum.intensity.tolist() == [
        100.0,
        200.0,
        300.0,
    ]

    assert spectrum.peak_wavelength == pytest.approx(1502.0)

    assert measurement.value == pytest.approx(300.0)

    assert measurement.metadata["peak_wavelength_nm"] == pytest.approx(1502.0)

    assert instrument.connected is False
