import asyncio
from datetime import UTC, datetime

import pytest

from app.acquisition.manager import (
    AcquisitionManager,
)
from app.devices.base import Instrument
from app.models.measurement import Measurement


class FakeInstrument(Instrument):
    def __init__(self) -> None:
        super().__init__(
            device_id="fake-001",
            name="Fake Instrument",
        )

        self.read_count = 0
        self.connect_count = 0
        self.disconnect_count = 0

    async def connect(self) -> None:
        self.connect_count += 1
        self._connected = True

    async def disconnect(self) -> None:
        self.disconnect_count += 1
        self._connected = False

    async def read(self) -> Measurement:
        if not self.connected:
            raise RuntimeError("not connected")

        await asyncio.sleep(0.001)

        self.read_count += 1

        return Measurement(
            timestamp=datetime.now(UTC),
            value=float(self.read_count),
            unit="V",
            sensor_id="sensor-1",
            device_id=self.device_id,
            measurement_type="voltage",
        )


@pytest.mark.asyncio
async def test_manager_starts_acquisition_and_buffers_measurements() -> None:
    instrument = FakeInstrument()

    manager = AcquisitionManager(
        instrument,
        buffer_size=10,
    )

    await manager.start()

    measurement = await manager.get(timeout=1.0)

    await manager.stop()

    assert measurement.value >= 1.0
    assert manager.stats.total_measurements >= 1
    assert instrument.connect_count == 1
    assert instrument.disconnect_count >= 1
    assert manager.running is False


@pytest.mark.asyncio
async def test_manager_drops_oldest_when_buffer_is_full() -> None:
    instrument = FakeInstrument()

    manager = AcquisitionManager(
        instrument,
        buffer_size=2,
        drop_oldest=True,
    )
    await manager.start()

    for _ in range(20):
        await asyncio.sleep(0.005)
        if manager.stats.dropped_measurements > 0:
            break

    await manager.stop()

    assert manager.stats.dropped_measurements > 0

    assert manager.buffer.qsize() == 2
