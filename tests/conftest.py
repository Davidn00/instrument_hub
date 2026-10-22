"""Shared fixtures for InstrumentHub automated tests."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def api_client() -> Iterator[TestClient]:
    """Provide an isolated FastAPI test client."""
    from app.main import app

    previous_overrides = app.dependency_overrides.copy()

    try:
        app.dependency_overrides.clear()

        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
