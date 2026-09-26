from pathlib import Path

import pandas as pd
import pytest

from app.acquisition.dataset_loader import (
    DatasetLoader,
    normalize_dataset,
)


def test_load_csv(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"

    dataframe = pd.DataFrame(
        {
            "timestamp": [
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:01Z",
            ],
            "value": [1.0, 2.0],
        }
    )

    dataframe.to_csv(
        path,
        index=False,
    )

    loader = DatasetLoader()

    result = loader.load(path)

    assert len(result) == 2
    assert list(result.columns) == [
        "timestamp",
        "value",
    ]


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
