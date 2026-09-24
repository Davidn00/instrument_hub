from pathlib import Path
from typing import Any

import pandas as pd

SUPPORTED_FORMATS = {
    ".csv",
    ".json",
    ".parquet",
}


class DatasetLoader:
    """
    Load instrumentation datasets from disk.
    """

    def load(self, path: str | Path) -> pd.DataFrame:
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"Dataset not found: {file_path}")

        extension = file_path.suffix.lower()

        if extension not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported dataset format: {extension}. "
                f"Supported formats: {sorted(SUPPORTED_FORMATS)}"
            )

        if extension == ".csv":
            return pd.read_csv(file_path)

        if extension == ".json":
            return pd.read_json(file_path)

        if extension == ".parquet":
            return pd.read_parquet(file_path)

        raise ValueError(f"Unable to load dataset: {file_path}")

    @staticmethod
    def validate_columns(
        dataframe: pd.DataFrame,
        required_columns: list[str],
    ) -> None:
        missing = [
            column for column in required_columns if column not in dataframe.columns
        ]

        if missing:
            raise ValueError(f"Dataset is missing required columns: {missing}")

    @staticmethod
    def metadata(
        dataframe: pd.DataFrame,
    ) -> dict[str, Any]:
        return {
            "rows": len(dataframe),
            "columns": list(dataframe.columns),
            "dtypes": {
                column: str(dtype) for column, dtype in dataframe.dtypes.items()
            },
        }


def normalize_dataset(
    dataframe: pd.DataFrame,
    value_column: str,
    timestamp_column: str | None = None,
) -> pd.DataFrame:
    """
    Normalize a dataset into a predictable representation.
    """

    if value_column not in dataframe.columns:
        raise ValueError(f"Value column '{value_column}' does not exist")

    result = dataframe.copy()

    result[value_column] = pd.to_numeric(
        result[value_column],
        errors="raise",
    )

    if timestamp_column is not None:
        if timestamp_column not in result.columns:
            raise ValueError(f"Timestamp column '{timestamp_column}' does not exist")

        result[timestamp_column] = pd.to_datetime(
            result[timestamp_column],
            errors="raise",
            utc=True,
        )

        result = result.sort_values(timestamp_column)

    return result.reset_index(drop=True)
