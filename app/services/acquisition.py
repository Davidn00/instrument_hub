from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.acquisition.manager import AcquisitionManager
from app.acquisition.protocols.ibsen import IBSENCalibration
from app.devices.base import Instrument
from app.devices.instruments.ibsen import IBSENInstrument
from app.devices.simulators import (
    SimulatedECGDevice,
    SimulatedEMGDevice,
    SimulatedFBGDevice,
    SimulatedPressureDevice,
    SimulatedSineDevice,
    SimulatedTemperatureDevice,
)
from app.realtime.websocket import WebSocketManager
from app.storage.models import DeviceRecord
from app.storage.repositories import (
    ChannelRepository,
    DeviceRepository,
    MeasurementRepository,
    SpectrumRepository,
)


@dataclass(slots=True)
class AcquisitionRuntime:
    instrument: Instrument
    manager: AcquisitionManager
    persistence_task: asyncio.Task[None]


class AcquisitionService:
    """Coordinates acquisition, persistence and real-time delivery."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        websocket_manager: WebSocketManager,
    ) -> None:
        self.session_factory = session_factory
        self.websocket_manager = websocket_manager

        self._runtimes: dict[str, AcquisitionRuntime] = {}

    def is_running(
        self,
        device_id: str,
    ) -> bool:
        runtime = self._runtimes.get(device_id)

        return runtime is not None and runtime.manager.running

    async def start(
        self,
        device: DeviceRecord,
    ) -> None:
        if self.is_running(device.device_id):
            return

        instrument = self._build_instrument(device)

        manager = AcquisitionManager(
            instrument,
            buffer_size=1024,
            reconnect_delay=1.0,
            max_reconnect_attempts=3,
            drop_oldest=True,
        )

        await manager.start()

        persistence_task = asyncio.create_task(
            self._persist_loop(
                device_id=device.device_id,
                instrument=instrument,
                manager=manager,
            ),
            name=f"persistence:{device.device_id}",
        )

        self._runtimes[device.device_id] = AcquisitionRuntime(
            instrument=instrument,
            manager=manager,
            persistence_task=persistence_task,
        )

        async with self.session_factory() as session:
            repository = DeviceRepository(session)

            await repository.update_status(
                device.device_id,
                "RUNNING",
            )

            await session.commit()

    async def stop(
        self,
        device_id: str,
    ) -> None:
        runtime = self._runtimes.get(device_id)

        if runtime is None:
            return

        await runtime.manager.stop()

        try:
            await runtime.persistence_task
        except asyncio.CancelledError:
            pass

        self._runtimes.pop(device_id, None)

        async with self.session_factory() as session:
            repository = DeviceRepository(session)

            await repository.update_status(
                device_id,
                "OFFLINE",
            )

            await session.commit()

    async def _persist_loop(
        self,
        *,
        device_id: str,
        instrument: Instrument,
        manager: AcquisitionManager,
    ) -> None:
        while manager.running or not manager.buffer.empty():
            try:
                measurement = await manager.get(
                    timeout=0.5,
                )
            except TimeoutError:
                continue

            async with self.session_factory() as session:
                measurement_repository = MeasurementRepository(session)

                channel_repository = ChannelRepository(session)

                await channel_repository.get_or_create(
                    device_id=measurement.device_id,
                    name=measurement.channel,
                    unit=measurement.unit,
                    metadata=measurement.metadata,
                )

                await measurement_repository.add(measurement)

                spectrum = getattr(
                    instrument,
                    "last_spectrum",
                    None,
                )

                spectrum_repository = SpectrumRepository(session)

                if spectrum is not None:
                    await spectrum_repository.add(spectrum)

                await session.commit()

            await self.websocket_manager.broadcast(
                {
                    "type": "measurement",
                    "data": {
                        "timestamp": (measurement.timestamp.isoformat()),
                        "device_id": measurement.device_id,
                        "channel": measurement.channel,
                        "value": measurement.value,
                        "unit": measurement.unit,
                        "quality": measurement.quality,
                        "metadata": measurement.metadata,
                    },
                }
            )

            if spectrum is not None:
                await self.websocket_manager.broadcast(
                    {
                        "type": "spectrum",
                        "data": {
                            "timestamp": (spectrum.timestamp.isoformat()),
                            "device_id": spectrum.device_id,
                            "wavelength": (spectrum.wavelength.tolist()),
                            "intensity": (spectrum.intensity.tolist()),
                            "wavelength_unit": (spectrum.wavelength_unit),
                            "intensity_unit": (spectrum.intensity_unit),
                        },
                    }
                )

    def _build_instrument(
        self,
        device: DeviceRecord,
    ) -> Instrument:
        metadata: dict[str, Any] = dict(device.metadata_)

        if device.device_type == "temperature":
            return SimulatedTemperatureDevice(device_id=device.device_id)

        if device.device_type == "pressure":
            return SimulatedPressureDevice(device_id=device.device_id)

        if device.device_type == "sine":
            return SimulatedSineDevice(device_id=device.device_id)

        if device.device_type == "ecg":
            return SimulatedECGDevice(device_id=device.device_id)

        if device.device_type == "emg":
            return SimulatedEMGDevice(device_id=device.device_id)

        if device.device_type == "fbg":
            return SimulatedFBGDevice(device_id=device.device_id)

        if device.device_type == "ibsen":
            calibration_data = metadata.get("calibration")

            if not isinstance(
                calibration_data,
                dict,
            ):
                raise ValueError("IBSEN device requires calibration metadata.")

            calibration = IBSENCalibration(
                a=float(calibration_data["a"]),
                b1=float(calibration_data["b1"]),
                b2=float(calibration_data["b2"]),
                b3=float(calibration_data["b3"]),
                b4=float(calibration_data["b4"]),
                b5=float(calibration_data["b5"]),
            )

            port = str(metadata["port"])

            baudrate = int(
                metadata.get(
                    "baudrate",
                    921600,
                )
            )

            expected_pixel_count = metadata.get("expected_pixel_count")

            return IBSENInstrument.from_serial(
                device_id=device.device_id,
                name=device.name,
                port=port,
                calibration=calibration,
                baudrate=baudrate,
                metadata=metadata,
                expected_pixel_count=(
                    int(expected_pixel_count)
                    if expected_pixel_count is not None
                    else None
                ),
            )

        raise ValueError(f"Unsupported device type: {device.device_type}")
