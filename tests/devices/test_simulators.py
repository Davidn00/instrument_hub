import pytest

from app.devices.simulators import (
    SimulatedECGDevice,
    SimulatedFBGDevice,
    SimulatedPressureDevice,
    SimulatedTemperatureDevice,
)


@pytest.mark.asyncio
async def test_temperature_device() -> None:
    device = SimulatedTemperatureDevice(
        device_id="temp-001",
    )

    await device.connect()

    measurement = await device.read()

    assert measurement.device_id == "temp-001"
    assert measurement.unit == "°C"
    assert measurement.measurement_type == "temperature"

    await device.disconnect()

    assert device.connected is False


@pytest.mark.asyncio
async def test_pressure_device() -> None:
    device = SimulatedPressureDevice(
        device_id="pressure-001",
    )

    await device.connect()

    measurement = await device.read()

    assert measurement.unit == "kPa"
    assert measurement.measurement_type == "pressure"


@pytest.mark.asyncio
async def test_device_requires_connection() -> None:
    device = SimulatedTemperatureDevice(
        device_id="temp-002",
    )

    with pytest.raises(RuntimeError):
        await device.read()


def test_ecg_acquisition() -> None:
    device = SimulatedECGDevice(
        device_id="ecg-001",
        sampling_rate=500.0,
    )

    signal = device.acquire(
        duration=2.0,
    )

    assert signal.number_of_samples == 1000
    assert signal.sampling_rate == 500.0


def test_fbg_acquisition() -> None:
    device = SimulatedFBGDevice(
        device_id="fbg-001",
        points=1000,
    )

    signal = device.acquire()

    assert signal.number_of_samples == 1000
    assert signal.unit == "a.u."
