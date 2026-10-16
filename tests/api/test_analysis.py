import math

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_fft_analysis_detects_dominant_frequency() -> None:
    sampling_rate = 100.0
    frequency = 5.0
    samples = [
        3.0 + math.sin(2.0 * math.pi * frequency * index / sampling_rate)
        for index in range(200)
    ]

    response = client.post(
        "/api/v1/analysis/fft",
        json={
            "samples": samples,
            "sampling_rate_hz": sampling_rate,
            "remove_mean": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sample_count"] == 200
    assert data["sampling_rate_hz"] == sampling_rate
    assert len(data["frequencies_hz"]) == 101
    assert len(data["amplitudes"]) == 101
    assert abs(data["dominant_frequency_hz"] - frequency) < 0.001


def test_fft_analysis_rejects_too_few_samples() -> None:
    response = client.post(
        "/api/v1/analysis/fft",
        json={
            "samples": [1.0, 2.0, 3.0],
            "sampling_rate_hz": 100.0,
        },
    )

    assert response.status_code == 422


def test_fft_analysis_rejects_invalid_sampling_rate() -> None:
    response = client.post(
        "/api/v1/analysis/fft",
        json={
            "samples": [float(index) for index in range(32)],
            "sampling_rate_hz": 0.0,
        },
    )

    assert response.status_code == 422
