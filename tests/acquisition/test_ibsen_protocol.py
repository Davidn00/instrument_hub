from collections import deque

import pytest

from app.acquisition.protocols.ibsen import (
    IBSENCalibration,
    IBSENCommandError,
    IBSENProtocol,
)


class FakeIBSENTransport:
    def __init__(
        self,
        responses: list[bytes],
    ) -> None:
        self.responses = deque(responses)
        self.writes: list[bytes] = []

    async def write(
        self,
        data: bytes,
    ) -> None:
        self.writes.append(data)

    async def read_byte(self) -> bytes:
        if not self.responses:
            raise TimeoutError

        value = self.responses.popleft()

        if len(value) != 1:
            raise AssertionError(f"Expected one byte, got {value!r}")

        return value

    async def read_until(
        self,
        delimiter: bytes = b"\r",
        *,
        max_bytes: int = 4096,
    ) -> bytes:
        if not self.responses:
            raise TimeoutError

        value = self.responses.popleft()

        if len(value) > max_bytes:
            raise ValueError("response too large")

        return value


@pytest.mark.asyncio
async def test_ibsen_initialize_discovers_device_and_configures_ascii_format() -> None:
    transport = FakeIBSENTransport(
        [
            b"JETI_MP_SERS\r",
            b"256\r",
            b"SN123\r",
            b"FW1.2\r",
            b"\x06",
        ]
    )

    protocol = IBSENProtocol(transport)

    info = await protocol.initialize()

    assert info.identification == ("JETI_MP_SERS")

    assert info.pixel_count == 256
    assert info.serial_number == "SN123"
    assert info.firmware_version == "FW1.2"

    assert transport.writes[-1] == (b"*CONFigure:FORMat 4\r")


@pytest.mark.asyncio
async def test_ibsen_read_spectrum_parses_ascii_format_4() -> None:
    transport = FakeIBSENTransport(
        [
            b"\x06",
            b"\x07",
            b"100\r",
            b"200\r",
            b"300\r",
        ]
    )

    protocol = IBSENProtocol(
        transport,
        pixel_count=3,
    )

    protocol.device_info = type(
        "Info",
        (),
        {"serial_number": "SN123"},
    )()

    spectrum = await protocol.read_spectrum()

    assert spectrum.intensity.tolist() == [
        100.0,
        200.0,
        300.0,
    ]

    assert spectrum.wavelength.tolist() == [
        0.0,
        1.0,
        2.0,
    ]

    assert transport.writes == [b"*READ 4\r"]


@pytest.mark.asyncio
async def test_ibsen_rejects_nak() -> None:
    transport = FakeIBSENTransport([b"\x15"])

    protocol = IBSENProtocol(transport)

    with pytest.raises(IBSENCommandError):
        await protocol.execute("*INIT")


def test_ibsen_calibration_polynomial_and_user_block() -> None:
    calibration = IBSENCalibration(
        a=1500.0,
        b1=1.0,
        b2=0.0,
        b3=0.0,
        b4=0.0,
        b5=0.0,
    )

    assert calibration.wavelength(25) == pytest.approx(1525.0)

    assert calibration.wavelengths(3) == pytest.approx(
        [
            1500.0,
            1501.0,
            1502.0,
        ]
    )

    fields = [
        b"1.0E+03",
        b"2.0E+00",
        b"3.0E-03",
        b"4.0E-06",
        b"5.0E-09",
        b"6.0E-12",
    ]

    block = b"".join(
        field.ljust(
            16,
            b" ",
        )
        for field in fields
    )

    parsed = IBSENCalibration.from_user_block(block)

    assert parsed.a == pytest.approx(1000.0)

    assert parsed.b1 == pytest.approx(2.0)

    assert parsed.b5 == pytest.approx(6e-12)
