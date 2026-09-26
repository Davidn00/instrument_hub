from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_simulated_devices() -> None:
    response = client.get("/api/v1/simulation/devices")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    device_types = {device["device_type"] for device in data}

    assert "temperature" in device_types
    assert "pressure" in device_types
    assert "ecg" in device_types
    assert "emg" in device_types
    assert "fbg" in device_types


def test_generate_sine_signal() -> None:
    response = client.post(
        "/api/v1/simulation/signals",
        json={
            "signal_type": "sine",
            "frequency": 10.0,
            "amplitude": 1.0,
            "sampling_rate": 100.0,
            "duration": 1.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["signal_type"] == "sine"
    assert data["sampling_rate"] == 100.0
    assert data["unit"] == "V"
    assert len(data["samples"]) == 100


def test_generate_ecg_signal() -> None:
    response = client.post(
        "/api/v1/simulation/signals",
        json={
            "signal_type": "ecg",
            "sampling_rate": 500.0,
            "duration": 2.0,
            "heart_rate": 72.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["signal_type"] == "ecg"
    assert len(data["samples"]) == 1000
    assert data["unit"] == "mV"


def test_generate_fbg_spectrum() -> None:
    response = client.post(
        "/api/v1/simulation/signals",
        json={
            "signal_type": "fbg_spectrum",
            "points": 1000,
            "center_wavelength": 1550.23,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["signal_type"] == "fbg_spectrum"
    assert len(data["samples"]) == 1000
    assert len(data["metadata"]["wavelengths_nm"]) == 1000


def test_temperature_measurement() -> None:
    response = client.post(
        "/api/v1/simulation/devices/temperature/measurement",
        json={
            "device_id": "temp-api-001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["device_id"] == "temp-api-001"
    assert data["unit"] == "°C"
    assert data["measurement_type"] == "temperature"


def test_pressure_measurement() -> None:
    response = client.post(
        "/api/v1/simulation/devices/pressure/measurement",
        json={
            "device_id": "pressure-api-001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["unit"] == "kPa"


def test_ecg_acquisition() -> None:
    response = client.post(
        "/api/v1/simulation/devices/ecg/acquire",
        json={
            "device_id": "ecg-api-001",
            "duration": 2.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["device_id"] == "ecg-api-001"
    assert data["sampling_rate"] == 500.0
    assert data["number_of_samples"] == 1000


def test_unknown_device() -> None:
    response = client.post(
        "/api/v1/simulation/devices/unknown/measurement",
        json={
            "device_id": "unknown-001",
        },
    )

    assert response.status_code == 404


def test_invalid_signal_request() -> None:
    response = client.post(
        "/api/v1/simulation/signals",
        json={
            "signal_type": "sine",
            "sampling_rate": 0,
        },
    )

    assert response.status_code == 422
