from collections.abc import AsyncIterator
from typing import Any

import pandas as pd


class DatasetPlayer:
    """
    Reproduce dataset rows as acquisition events.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        value_column: str,
        timestamp_column: str | None = None,
        realtime: bool = False,
    ) -> None:
        self.dataframe = dataframe
        self.value_column = value_column
        self.timestamp_column = timestamp_column
        self.realtime = realtime

    async def play(self) -> AsyncIterator[dict[str, Any]]:
        previous_timestamp = None

        for raw_row in self.dataframe.to_dict(orient="records"):
            row: dict[str, Any] = {str(key): value for key, value in raw_row.items()}

            if self.realtime and self.timestamp_column is not None:
                current_timestamp = row[self.timestamp_column]

                if previous_timestamp is not None:
                    delay = (current_timestamp - previous_timestamp).total_seconds()

                    if delay > 0:
                        import asyncio

                        await asyncio.sleep(delay)

                previous_timestamp = current_timestamp

            yield row
