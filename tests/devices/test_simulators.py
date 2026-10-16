import asyncio

import pytest

from app.devices.simulators import (
    SimulatedECGDevice,
    SimulatedFBGDevice,
    SimulatedPressureDevice,
    SimulatedSineDevice,
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


@pytest.mark.asyncio
async def test_fbg_read_generates_associated_spectrum() -> None:
    device = SimulatedFBGDevice(
        device_id="fbg-live-001",
        points=500,
        noise_amplitude=0.0,
    )

    await device.connect()

    measurement = await device.read()
    spectrum = device.get_spectrum_for_measurement(
        measurement.timestamp,
    )

    assert spectrum is not None
    assert measurement.device_id == "fbg-live-001"
    assert measurement.channel == "FBG-1"
    assert measurement.unit == "nm"

    assert spectrum.device_id == measurement.device_id
    assert spectrum.timestamp == measurement.timestamp
    assert len(spectrum.wavelength) == 500
    assert len(spectrum.intensity) == 500

    assert spectrum.wavelength_unit == "nm"
    assert spectrum.intensity_unit == "a.u."

    assert measurement.value == spectrum.peak_wavelength

    # La asociación se consume una sola vez.
    assert (
        device.get_spectrum_for_measurement(
            measurement.timestamp,
        )
        is None
    )

    await device.disconnect()


@pytest.mark.asyncio
async def test_sine_device_generates_changing_measurements() -> None:
    device = SimulatedSineDevice(
        device_id="sine-fft-test",
        frequency=1.0,
        amplitude=1.0,
        sampling_rate=10.0,
    )

    await device.connect()

    first = await device.read()
    await asyncio.sleep(0.05)
    second = await device.read()

    assert first.device_id == "sine-fft-test"
    assert second.device_id == "sine-fft-test"
    assert first.unit == "V"
    assert second.unit == "V"
    assert first.value != second.value

    await device.disconnect()
