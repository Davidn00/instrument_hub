from datetime import UTC, datetime, timedelta

import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.models.spectrum import Spectrum
from app.storage.db import get_db
from app.storage.repositories import SpectrumRepository


def test_fbg_analysis_returns_peaks_and_tracking(
    monkeypatch,
) -> None:
    device_id = "fbg-api-test"
    wavelength = np.linspace(1549.0, 1551.0, 501)
    base_time = datetime(2026, 10, 16, tzinfo=UTC)

    spectra = []

    for index in range(5):
        center = 1550.0 + index * 0.01
        intensity = np.exp(-0.5 * ((wavelength - center) / 0.04) ** 2)

        spectra.append(
            Spectrum(
                timestamp=base_time + timedelta(seconds=index),
                device_id=device_id,
                wavelength=wavelength.copy(),
                intensity=intensity,
                wavelength_unit="nm",
                intensity_unit="a.u.",
                metadata={"test_spectrum": index},
            )
        )

    async def fake_list(
        self,
        *,
        device_id=None,
        start=None,
        end=None,
        limit=100,
        offset=0,
    ):
        assert device_id == "fbg-api-test"

        # Simulate the repository's newest-first ordering.
        return list(reversed(spectra))[:limit][offset:]

    async def override_get_db():
        yield None

    monkeypatch.setattr(SpectrumRepository, "list", fake_list)
    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/fbg/analyze",
                json={
                    "device_id": device_id,
                    "history_limit": 100,
                    "noise_reduction": True,
                    "noise_window_length": 11,
                    "noise_polyorder": 3,
                    "refinement": "quadratic",
                },
            )

        assert response.status_code == 200

        data = response.json()

        assert data["device_id"] == device_id
        assert len(data["spectrum"]["wavelength"]) == 501
        assert len(data["filtered_intensity"]) == 501
        assert len(data["peaks"]) >= 1
        assert data["peak_wavelength_nm"] is not None
        assert abs(data["peak_wavelength_nm"] - 1550.04) < 0.03
        assert data["analyzed_spectra_count"] == 5
        assert len(data["tracking_points"]) == 5
        assert data["reference_wavelength_nm"] is not None
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
