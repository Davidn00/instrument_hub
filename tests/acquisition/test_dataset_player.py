import pandas as pd
import pytest

from app.acquisition.dataset_player import DatasetPlayer


@pytest.mark.asyncio
async def test_playback_without_realtime() -> None:
    dataframe = pd.DataFrame(
        {
            "timestamp": [
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:01Z",
                "2026-01-01T00:00:02Z",
            ],
            "value": [1.0, 2.0, 3.0],
        }
    )

    player = DatasetPlayer(
        dataframe=dataframe,
        value_column="value",
        timestamp_column="timestamp",
        realtime=False,
    )

    values = []

    async for row in player.play():
        values.append(row["value"])

    assert values == [1.0, 2.0, 3.0]


@pytest.mark.asyncio
async def test_realtime_playback_respects_timestamps() -> None:
    dataframe = pd.DataFrame(
        {
            "timestamp": [
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:01Z",
                "2026-01-01T00:00:03Z",
            ],
            "value": [10.0, 20.0, 30.0],
        }
    )

    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    player = DatasetPlayer(
        dataframe=dataframe,
        value_column="value",
        timestamp_column="timestamp",
        realtime=True,
        sleeper=fake_sleep,
    )

    values = []

    async for row in player.play():
        values.append(row["value"])

    assert values == [10.0, 20.0, 30.0]
    assert delays == [1.0, 2.0]


@pytest.mark.asyncio
async def test_playback_speed() -> None:
    dataframe = pd.DataFrame(
        {
            "timestamp": [
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:04Z",
            ],
            "value": [1.0, 2.0],
        }
    )

    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    player = DatasetPlayer(
        dataframe=dataframe,
        value_column="value",
        timestamp_column="timestamp",
        realtime=True,
        speed=2.0,
        sleeper=fake_sleep,
    )

    async for _ in player.play():
        pass

    assert delays == [2.0]


@pytest.mark.asyncio
async def test_negative_time_difference_does_not_sleep() -> None:
    dataframe = pd.DataFrame(
        {
            "timestamp": [
                "2026-01-01T00:00:02Z",
                "2026-01-01T00:00:01Z",
            ],
            "value": [1.0, 2.0],
        }
    )

    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    player = DatasetPlayer(
        dataframe=dataframe,
        value_column="value",
        timestamp_column="timestamp",
        realtime=True,
        sleeper=fake_sleep,
    )

    async for _ in player.play():
        pass

    assert delays == [0.0]


def test_empty_dataset_rejected() -> None:
    dataframe = pd.DataFrame(columns=["timestamp", "value"])

    with pytest.raises(ValueError):
        DatasetPlayer(
            dataframe=dataframe,
            value_column="value",
        )


def test_invalid_speed_rejected() -> None:
    dataframe = pd.DataFrame(
        {
            "value": [1.0],
        }
    )

    with pytest.raises(ValueError):
        DatasetPlayer(
            dataframe=dataframe,
            value_column="value",
            speed=0.0,
        )


def test_missing_value_column_rejected() -> None:
    dataframe = pd.DataFrame(
        {
            "other": [1.0],
        }
    )

    with pytest.raises(ValueError):
        DatasetPlayer(
            dataframe=dataframe,
            value_column="value",
        )


def test_missing_timestamp_column_rejected() -> None:
    dataframe = pd.DataFrame(
        {
            "value": [1.0],
        }
    )

    with pytest.raises(ValueError):
        DatasetPlayer(
            dataframe=dataframe,
            value_column="value",
            timestamp_column="timestamp",
        )
