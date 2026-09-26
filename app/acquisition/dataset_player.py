import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

import pandas as pd

SleepFunction = Callable[[float], Awaitable[None]]


class DatasetPlayer:
    """
    Reproduce un dataset como si fueran eventos de adquisición.

    realtime=False:
        Emite los datos inmediatamente.

    realtime=True:
        Respeta el intervalo temporal entre muestras.

    speed:
        Factor de velocidad de reproducción.

        speed=1.0 -> velocidad original
        speed=2.0 -> dos veces más rápido
        speed=0.5 -> dos veces más lento
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        value_column: str,
        timestamp_column: str | None = None,
        realtime: bool = False,
        speed: float = 1.0,
        sleeper: SleepFunction | None = None,
    ) -> None:
        if dataframe.empty:
            raise ValueError("dataframe cannot be empty")

        if value_column not in dataframe.columns:
            raise ValueError(f"value column '{value_column}' does not exist")

        if timestamp_column is not None and timestamp_column not in dataframe.columns:
            raise ValueError(f"timestamp column '{timestamp_column}' does not exist")

        if speed <= 0:
            raise ValueError("speed must be greater than zero")

        self.dataframe = dataframe.copy()
        self.value_column = value_column
        self.timestamp_column = timestamp_column
        self.realtime = realtime
        self.speed = speed

        self._sleep = sleeper or asyncio.sleep

        if timestamp_column is not None:
            self.dataframe[timestamp_column] = pd.to_datetime(
                self.dataframe[timestamp_column],
                utc=True,
                errors="raise",
            )

    def _delay_between(
        self,
        previous: pd.Timestamp,
        current: pd.Timestamp,
    ) -> float:
        """
        Calculate playback delay in seconds.
        """

        elapsed = (current - previous).total_seconds()

        return max(0.0, elapsed / self.speed)

    async def play(self) -> AsyncIterator[dict[str, Any]]:
        """
        Asynchronously reproduce the dataset.
        """

        previous_timestamp: pd.Timestamp | None = None

        records = self.dataframe.to_dict(orient="records")
        for raw_row in records:
            row: dict[str, Any] = {str(key): value for key, value in raw_row.items()}
            if self.realtime and self.timestamp_column is not None:
                current_timestamp = pd.Timestamp(row[self.timestamp_column])

                if previous_timestamp is not None:
                    delay = self._delay_between(
                        previous_timestamp,
                        current_timestamp,
                    )

                    await self._sleep(delay)

                previous_timestamp = current_timestamp

            yield row
