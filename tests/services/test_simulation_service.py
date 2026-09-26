import numpy as np
import pytest

from app.services.simulation import (
    SimulationService,
    UnknownSimulationDeviceError,
    UnsupportedAcquisitionError,
)


def test_service_lists_devices() -> None:
    service = SimulationService()

    devices = service.list_devices()

    assert len(devices) >= 6

    device_types = {device["device_type"] for device in devices}

    assert {
        "temperature",
        "pressure",
        "sine",
        "ecg",
        "emg",
        "fbg",
    }.issubset(device_types)


@pytest.mark.parametrize(
    "signal_type",
    [
        "sine",
        "noise",
        "ecg",
        "emg",
        "fbg_spectrum",
    ],
)
def test_signal_generation(
    signal_type: str,
) -> None:
    service = SimulationService()

    parameters = {
        "sine": {
            "frequency": 10.0,
            "amplitude": 1.0,
            "sampling_rate": 100.0,
            "duration": 1.0,
        },
        "noise": {
            "amplitude": 1.0,
            "sampling_rate": 100.0,
            "duration": 1.0,
            "seed": 42,
        },
        "ecg": {
            "sampling_rate": 500.0,
            "duration": 2.0,
            "heart_rate": 72.0,
            "amplitude": 1.0,
            "noise_amplitude": 0.01,
            "seed": 42,
        },
        "emg": {
            "sampling_rate": 1000.0,
            "duration": 2.0,
            "amplitude": 1.0,
            "burst_frequency": 50.0,
            "noise_amplitude": 0.05,
            "seed": 42,
        },
        "fbg_spectrum": {
            "center_wavelength": 1550.23,
            "wavelength_start": 1548.0,
            "wavelength_end": 1552.0,
            "points": 500,
            "amplitude": 1.0,
            "linewidth": 0.08,
            "noise_amplitude": 0.01,
            "seed": 42,
        },
    }

    generated = service.generate_signal(
        signal_type=signal_type,
        parameters=parameters[signal_type],
    )

    assert generated.signal_type == signal_type
    assert len(generated.samples) > 0
    assert isinstance(
        generated.samples,
        np.ndarray,
    )


@pytest.mark.asyncio
async def test_service_reads_temperature() -> None:
    service = SimulationService()

    measurement = await service.read_measurement(
        device_type="temperature",
        device_id="temp-service-001",
    )

    assert measurement.device_id == "temp-service-001"

    assert measurement.measurement_type == "temperature"


@pytest.mark.asyncio
async def test_unknown_device_rejected() -> None:
    service = SimulationService()

    with pytest.raises(UnknownSimulationDeviceError):
        await service.read_measurement(
            device_type="invalid",
            device_id="invalid-001",
        )


def test_unsupported_acquisition_rejected() -> None:
    service = SimulationService()

    with pytest.raises(UnsupportedAcquisitionError):
        service.acquire_signal(
            device_type="temperature",
            device_id="temp-001",
            duration=1.0,
        )
