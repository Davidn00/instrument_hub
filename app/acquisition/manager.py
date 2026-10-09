import asyncio
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.devices.base import Instrument
from app.models.measurement import Measurement


@dataclass(slots=True)
class AcquisitionStats:
    """Runtime metrics for one acquisition session."""

    total_measurements: int = 0
    dropped_measurements: int = 0
    errors: int = 0
    reconnects: int = 0
    started_at: datetime | None = None
    last_measurement_at: datetime | None = None
    _started_monotonic: float | None = None

    @property
    def elapsed_seconds(self) -> float:
        if self._started_monotonic is None:
            return 0.0

        return max(
            0.0,
            time.monotonic() - self._started_monotonic,
        )

    @property
    def throughput(self) -> float:
        elapsed = self.elapsed_seconds

        if elapsed <= 0:
            return 0.0

        return self.total_measurements / elapsed


class AcquisitionManager:
    """Owns the lifecycle and asynchronous acquisition loop."""

    def __init__(
        self,
        instrument: Instrument,
        *,
        buffer_size: int = 1024,
        reconnect_delay: float = 1.0,
        max_reconnect_attempts: int = 0,
        drop_oldest: bool = True,
    ) -> None:
        if buffer_size <= 0:
            raise ValueError("buffer_size must be greater than zero")

        if reconnect_delay < 0:
            raise ValueError("reconnect_delay cannot be negative")

        if max_reconnect_attempts < 0:
            raise ValueError("max_reconnect_attempts cannot be negative")

        self.instrument = instrument

        self.buffer: asyncio.Queue[Measurement] = asyncio.Queue(maxsize=buffer_size)

        self.reconnect_delay = reconnect_delay
        self.max_reconnect_attempts = max_reconnect_attempts
        self.drop_oldest = drop_oldest

        self.stats = AcquisitionStats()

        self._stop_event = asyncio.Event()

        self._task: asyncio.Task[None] | None = None

        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    async def connect(self) -> None:
        await self.instrument.connect()

    async def disconnect(self) -> None:
        await self.instrument.disconnect()

    async def start(self) -> None:
        if self.running:
            return

        await self.connect()

        self.stats = AcquisitionStats(
            started_at=datetime.now(UTC),
            _started_monotonic=time.monotonic(),
        )

        self._stop_event.clear()
        self._running = True

        self._task = asyncio.create_task(
            self._acquisition_loop(),
            name=(f"acquisition:{self.instrument.device_id}"),
        )

    async def stop(self) -> None:
        if not self.running:
            if self.instrument.connected:
                await self.disconnect()

            return

        self._stop_event.set()

        task = self._task

        if task is not None:
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

        self._task = None
        self._running = False

        if self.instrument.connected:
            await self.disconnect()

    async def get(
        self,
        timeout: float | None = None,
    ) -> Measurement:
        if timeout is None:
            return await self.buffer.get()

        return await asyncio.wait_for(
            self.buffer.get(),
            timeout=timeout,
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "device_id": self.instrument.device_id,
            "running": self.running,
            "connected": self.instrument.connected,
            "buffer_size": self.buffer.qsize(),
            "buffer_capacity": self.buffer.maxsize,
            "total_measurements": (self.stats.total_measurements),
            "dropped_measurements": (self.stats.dropped_measurements),
            "errors": self.stats.errors,
            "reconnects": self.stats.reconnects,
            "throughput_per_second": (self.stats.throughput),
            "started_at": (
                self.stats.started_at.isoformat()
                if self.stats.started_at is not None
                else None
            ),
            "last_measurement_at": (
                self.stats.last_measurement_at.isoformat()
                if self.stats.last_measurement_at is not None
                else None
            ),
        }

    async def _acquisition_loop(self) -> None:
        reconnect_attempts = 0

        try:
            while not self._stop_event.is_set():
                try:
                    measurement = await self.instrument.read()

                    reconnect_attempts = 0

                    if measurement.timestamp.tzinfo is None:
                        measurement.timestamp = measurement.timestamp.replace(
                            tzinfo=UTC
                        )

                    self.stats.total_measurements += 1

                    self.stats.last_measurement_at = measurement.timestamp

                    self._put_buffered(measurement)

                    # Give the event loop time to process other tasks.
                    await asyncio.sleep(0.1)

                except asyncio.CancelledError:
                    raise

                except Exception:
                    self.stats.errors += 1

                    if self._stop_event.is_set():
                        break

                    reconnect_attempts += 1

                    if (
                        self.max_reconnect_attempts > 0
                        and reconnect_attempts > self.max_reconnect_attempts
                    ):
                        break

                    try:
                        await self._reconnect(reconnect_attempts)

                    except asyncio.CancelledError:
                        raise

                    except Exception:
                        self.stats.errors += 1

        finally:
            self._running = False

            if self.instrument.connected:
                try:
                    await self.instrument.disconnect()

                except Exception:
                    self.stats.errors += 1

    def _put_buffered(
        self,
        measurement: Measurement,
    ) -> None:
        if not self.buffer.full():
            self.buffer.put_nowait(measurement)
            return

        if not self.drop_oldest:
            self.stats.dropped_measurements += 1
            return

        try:
            self.buffer.get_nowait()

        except asyncio.QueueEmpty:
            pass

        else:
            self.stats.dropped_measurements += 1

        self.buffer.put_nowait(measurement)

    async def _reconnect(
        self,
        reconnect_attempt: int,
    ) -> None:
        try:
            await self.instrument.disconnect()

        except Exception:
            pass

        if self._stop_event.is_set():
            return

        delay = self.reconnect_delay * max(1, reconnect_attempt)

        await asyncio.sleep(delay)

        if self._stop_event.is_set():
            return

        await self.instrument.connect()

        self.stats.reconnects += 1
