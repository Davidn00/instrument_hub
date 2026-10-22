import numpy as np
import pytest

from app.acquisition.protocols.ibsen import (
    IBSENCalibration,
    IBSENCommandError,
    IBSENProtocol,
    IBSENProtocolError,
)
from app.devices.instruments.ibsen import IBSENInstrument
from app.devices.simulators.ibsen_hardware import IBSENHardwareSimulator


def make_instrument(
    simulator: IBSENHardwareSimulator,
) -> IBSENInstrument:
    """Build the real driver around the simulated transport."""
    return IBSENInstrument(
        device_id="ibsen-simulator-001",
        name="IBSEN I-MON Simulator",
        transport=simulator,
        expected_pixel_count=simulator.pixel_count,
        calibration=IBSENCalibration(
            a=1500.0,
            b1=0.1,
            b2=0.0,
            b3=0.0,
            b4=0.0,
            b5=0.0,
        ),
    )


@pytest.mark.asyncio
async def test_simulator_initializes_real_ibsen_driver() -> None:
    simulator = IBSENHardwareSimulator(
        pixel_count=128,
        seed=10,
    )
    instrument = make_instrument(simulator)

    await instrument.connect()

    try:
        assert instrument.connected
        assert instrument.protocol.device_info is not None
        assert instrument.protocol.device_info.pixel_count == 128
        assert instrument.protocol.device_info.serial_number == "SIM-IBSEN-001"
        assert simulator.connected
    finally:
        await instrument.disconnect()

    assert not instrument.connected
    assert not simulator.connected


@pytest.mark.asyncio
async def test_simulator_returns_calibrated_spectrum() -> None:
    simulator = IBSENHardwareSimulator(
        pixel_count=128,
        peak_pixel=64,
        noise_std=0,
    )
    instrument = make_instrument(simulator)

    await instrument.connect()

    try:
        spectrum = await instrument.read_spectrum()

        assert spectrum.number_of_pixels == 128
        assert spectrum.wavelength[0] == pytest.approx(1500.0)
        assert spectrum.wavelength[1] == pytest.approx(1500.1)
        assert np.all(np.isfinite(spectrum.intensity))
        assert np.all(spectrum.intensity >= 0)
        assert np.all(spectrum.intensity <= 65535)
        assert spectrum.peak_intensity > 40000
        assert simulator.spectra_generated == 1
    finally:
        await instrument.disconnect()


@pytest.mark.asyncio
async def test_simulator_can_reject_a_command_with_nak() -> None:
    simulator = IBSENHardwareSimulator(
        nak_commands={"*INIT"},
    )
    instrument = make_instrument(simulator)

    await instrument.connect()

    try:
        with pytest.raises(IBSENCommandError):
            await instrument.start()
    finally:
        await instrument.disconnect()


@pytest.mark.asyncio
async def test_simulator_detects_malformed_spectrum_response() -> None:
    simulator = IBSENHardwareSimulator(
        pixel_count=16,
        malformed_next_spectrum=True,
    )
    instrument = make_instrument(simulator)

    await instrument.connect()

    try:
        with pytest.raises(IBSENProtocolError):
            await instrument.read_spectrum()
    finally:
        await instrument.disconnect()


@pytest.mark.asyncio
async def test_simulator_rejects_spectrum_before_format_configuration() -> None:
    simulator = IBSENHardwareSimulator(pixel_count=8)
    protocol = IBSENProtocol(
        simulator,
        pixel_count=8,
    )

    await simulator.connect()

    try:
        with pytest.raises(IBSENCommandError):
            await protocol.read_spectrum()
    finally:
        await simulator.disconnect()


@pytest.mark.asyncio
async def test_simulator_validates_configuration() -> None:
    with pytest.raises(ValueError):
        IBSENHardwareSimulator(pixel_count=0)

    with pytest.raises(ValueError):
        IBSENHardwareSimulator(noise_std=-1)
