from pathlib import Path

import pandas as pd
import pytest

from app.acquisition.dataset_loader import (
    DatasetLoader,
    normalize_dataset,
)


def create_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": [
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:01Z",
                "2026-01-01T00:00:02Z",
            ],
            "value": [1.0, 2.0, 3.0],
        }
    )


def test_load_csv(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"

    dataframe = create_dataframe()

    dataframe.to_csv(
        path,
        index=False,
    )

    loader = DatasetLoader()

    result = loader.load(path)

    assert len(result) == 3
    assert "value" in result.columns


def test_load_json(tmp_path: Path) -> None:
    path = tmp_path / "data.json"

    dataframe = create_dataframe()

    dataframe.to_json(
        path,
        orient="records",
    )

    loader = DatasetLoader()

    result = loader.load(path)

    assert len(result) == 3
    assert "value" in result.columns


def test_load_parquet(tmp_path: Path) -> None:
    path = tmp_path / "data.parquet"

    dataframe = create_dataframe()

    dataframe.to_parquet(
        path,
        index=False,
    )

    loader = DatasetLoader()

    result = loader.load(path)

    assert len(result) == 3
    assert "value" in result.columns


def test_unsupported_format(tmp_path: Path) -> None:
    path = tmp_path / "data.txt"

    path.write_text("invalid")

    loader = DatasetLoader()

    with pytest.raises(ValueError):
        loader.load(path)


def test_normalize_dataset() -> None:
    dataframe = pd.DataFrame(
        {
            "timestamp": [
                "2026-01-01T00:00:02Z",
                "2026-01-01T00:00:01Z",
            ],
            "value": ["2.0", "1.0"],
        }
    )

    result = normalize_dataset(
        dataframe,
        value_column="value",
        timestamp_column="timestamp",
    )

    assert result["value"].tolist() == [
        1.0,
        2.0,
    ]

    assert result["timestamp"].is_monotonic_increasing
