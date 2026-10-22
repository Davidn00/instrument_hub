from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.dialects import postgresql

from app.storage.repositories import (
    MeasurementRepository,
    SpectrumRepository,
)


@pytest.mark.asyncio
async def test_measurement_repository_applies_filters_and_pagination() -> None:
    session = AsyncMock()

    result = Mock()
    result.scalars.return_value.all.return_value = []
    session.execute.return_value = result

    start = datetime(2026, 10, 20, 10, 0, tzinfo=UTC)
    end = datetime(2026, 10, 20, 11, 0, tzinfo=UTC)

    measurements = await MeasurementRepository(session).list(
        device_id="device-test-01",
        channel="temperature",
        start=start,
        end=end,
        limit=25,
        offset=50,
    )

    assert measurements == []
    session.execute.assert_awaited_once()

    statement = session.execute.await_args.args[0]
    compiled = statement.compile(dialect=postgresql.dialect())
    sql = str(compiled).lower()

    assert "measurements.device_id =" in sql
    assert "measurements.channel =" in sql
    assert "measurements.timestamp >=" in sql
    assert "measurements.timestamp <=" in sql
    assert "order by measurements.timestamp desc" in sql
    assert "limit" in sql
    assert "offset" in sql

    assert compiled.params["device_id_1"] == "device-test-01"
    assert compiled.params["channel_1"] == "temperature"
    assert compiled.params["timestamp_1"] == start
    assert compiled.params["timestamp_2"] == end
    assert compiled.params["param_1"] == 50 or 50 in compiled.params.values()


@pytest.mark.asyncio
async def test_measurement_repository_supports_unfiltered_listing() -> None:
    session = AsyncMock()

    result = Mock()
    result.scalars.return_value.all.return_value = []
    session.execute.return_value = result

    measurements = await MeasurementRepository(session).list()

    assert measurements == []

    statement = session.execute.await_args.args[0]
    sql = str(statement.compile(dialect=postgresql.dialect())).lower()

    assert "where" not in sql
    assert "order by measurements.timestamp desc" in sql


@pytest.mark.asyncio
async def test_spectrum_repository_applies_device_and_time_filters() -> None:
    session = AsyncMock()

    result = Mock()
    result.scalars.return_value.all.return_value = []
    session.execute.return_value = result

    start = datetime(2026, 10, 20, 10, 0, tzinfo=UTC)
    end = datetime(2026, 10, 20, 11, 0, tzinfo=UTC)

    spectra = await SpectrumRepository(session).list(
        device_id="ibsen-test-01",
        start=start,
        end=end,
        limit=10,
        offset=5,
    )

    assert spectra == []

    statement = session.execute.await_args.args[0]
    compiled = statement.compile(dialect=postgresql.dialect())
    sql = str(compiled).lower()

    assert "spectra.device_id =" in sql
    assert "spectra.timestamp >=" in sql
    assert "spectra.timestamp <=" in sql
    assert "order by spectra.timestamp desc" in sql
    assert "limit" in sql
    assert "offset" in sql

    assert "ibsen-test-01" in compiled.params.values()
    assert start in compiled.params.values()
    assert end in compiled.params.values()
