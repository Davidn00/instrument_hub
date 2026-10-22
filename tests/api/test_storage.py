from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import numpy as np
import pytest

from app.api.v1.routes import measurements as measurements_route
from app.api.v1.routes import spectra as spectra_route
from app.main import app
from app.models.measurement import Measurement
from app.models.spectrum import Spectrum
from app.storage.db import get_db


@pytest.fixture
def fake_db_session(monkeypatch):
    """Override the database dependency with an isolated mock session."""
    session = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())

    async def override_get_db():
        yield session

    monkeypatch.setitem(
        app.dependency_overrides,
        get_db,
        override_get_db,
    )
    return session


def test_list_measurements_returns_repository_data(
    api_client,
    fake_db_session,
    monkeypatch,
) -> None:
    timestamp = datetime(2026, 10, 20, 12, 0, tzinfo=UTC)
    expected = Measurement(
        timestamp=timestamp,
        device_id="integration-device-01",
        channel="temperature",
        value=23.5,
        unit="°C",
        quality="GOOD",
        metadata={"source": "test"},
    )
    captured = {}

    class FakeMeasurementRepository:
        def __init__(self, session):
            assert session is fake_db_session

        async def list(self, **kwargs):
            captured.update(kwargs)
            return [expected]

    monkeypatch.setattr(
        measurements_route,
        "MeasurementRepository",
        FakeMeasurementRepository,
    )

    response = api_client.get(
        "/api/v1/measurements",
        params={
            "device_id": "integration-device-01",
            "channel": "temperature",
            "limit": 25,
            "offset": 0,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["device_id"] == "integration-device-01"
    assert data[0]["channel"] == "temperature"
    assert data[0]["value"] == 23.5
    assert data[0]["metadata"] == {"source": "test"}

    assert captured["device_id"] == "integration-device-01"
    assert captured["channel"] == "temperature"
    assert captured["limit"] == 25
    assert captured["offset"] == 0


def test_measurement_limit_above_maximum_returns_422(
    api_client,
    fake_db_session,
) -> None:
    response = api_client.get(
        "/api/v1/measurements",
        params={"limit": 5001},
    )

    assert response.status_code == 422


def test_list_spectra_returns_repository_data(
    api_client,
    fake_db_session,
    monkeypatch,
) -> None:
    timestamp = datetime(2026, 10, 20, 12, 0, tzinfo=UTC)
    expected = Spectrum(
        timestamp=timestamp,
        device_id="ibsen-integration-01",
        wavelength=np.array([1549.0, 1550.0, 1551.0]),
        intensity=np.array([10.0, 100.0, 20.0]),
        metadata={"source": "simulator"},
    )

    class FakeSpectrumRepository:
        def __init__(self, session):
            assert session is fake_db_session

        async def list(self, **kwargs):
            assert kwargs["device_id"] == "ibsen-integration-01"
            assert kwargs["limit"] == 10
            return [expected]

    monkeypatch.setattr(
        spectra_route,
        "SpectrumRepository",
        FakeSpectrumRepository,
    )

    response = api_client.get(
        "/api/v1/spectra",
        params={
            "device_id": "ibsen-integration-01",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["device_id"] == "ibsen-integration-01"
    assert data[0]["wavelength"] == [1549.0, 1550.0, 1551.0]
    assert data[0]["intensity"] == [10.0, 100.0, 20.0]
    assert data[0]["metadata"] == {"source": "simulator"}


def test_create_spectrum_commits_and_returns_created_resource(
    api_client,
    fake_db_session,
    monkeypatch,
) -> None:
    record_id = uuid4()
    captured = {}

    class FakeSpectrumRepository:
        def __init__(self, session):
            assert session is fake_db_session

        async def add(self, spectrum):
            captured["spectrum"] = spectrum
            return SimpleNamespace(id=record_id)

    monkeypatch.setattr(
        spectra_route,
        "SpectrumRepository",
        FakeSpectrumRepository,
    )

    response = api_client.post(
        "/api/v1/spectra",
        json={
            "timestamp": "2026-10-20T12:00:00Z",
            "device_id": "ibsen-api-01",
            "wavelength": [1549.0, 1550.0, 1551.0],
            "intensity": [10.0, 100.0, 20.0],
            "wavelength_unit": "nm",
            "intensity_unit": "counts",
            "metadata": {"test": True},
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == str(record_id)
    assert data["device_id"] == "ibsen-api-01"
    assert data["wavelength"] == [1549.0, 1550.0, 1551.0]
    assert data["intensity"] == [10.0, 100.0, 20.0]
    assert data["metadata"] == {"test": True}

    assert captured["spectrum"].number_of_pixels == 3
    fake_db_session.commit.assert_awaited_once()


def test_create_spectrum_rejects_mismatched_arrays(
    api_client,
    fake_db_session,
    monkeypatch,
) -> None:
    async def unexpected_add(self, spectrum):
        pytest.fail("Invalid spectrum must not reach the repository")

    monkeypatch.setattr(
        spectra_route,
        "SpectrumRepository",
        type(
            "UnexpectedSpectrumRepository",
            (),
            {
                "__init__": lambda self, session: None,
                "add": unexpected_add,
            },
        ),
    )

    response = api_client.post(
        "/api/v1/spectra",
        json={
            "timestamp": "2026-10-20T12:00:00Z",
            "device_id": "ibsen-api-invalid",
            "wavelength": [1549.0, 1550.0],
            "intensity": [10.0],
        },
    )

    assert response.status_code == 422
    fake_db_session.commit.assert_not_awaited()
