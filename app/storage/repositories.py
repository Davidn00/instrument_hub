from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.measurement import Measurement
from app.models.spectrum import Spectrum
from app.storage.mappers import (
    measurement_to_record,
    record_to_measurement,
    record_to_spectrum,
    spectrum_to_record,
)
from app.storage.models import (
    ChannelRecord,
    DeviceRecord,
    ExperimentRecord,
    MeasurementRecord,
    SpectrumRecord,
)


class DeviceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[DeviceRecord]:
        result = await self.session.execute(
            select(DeviceRecord).order_by(DeviceRecord.created_at)
        )

        return list(result.scalars().all())

    async def get_by_device_id(
        self,
        device_id: str,
    ) -> DeviceRecord | None:
        result = await self.session.execute(
            select(DeviceRecord).where(DeviceRecord.device_id == device_id)
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        device_id: str,
        name: str,
        device_type: str,
        interface: str | None,
        metadata: dict[str, Any],
    ) -> DeviceRecord:
        device = DeviceRecord(
            device_id=device_id,
            name=name,
            device_type=device_type,
            interface=interface,
            metadata_=metadata,
        )

        self.session.add(device)
        await self.session.flush()

        return device

    async def update_status(
        self,
        device_id: str,
        status: str,
    ) -> None:
        device = await self.get_by_device_id(device_id)

        if device is None:
            raise ValueError(f"Device '{device_id}' does not exist.")

        device.status = status
        await self.session.flush()


class ChannelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(
        self,
        *,
        device_id: str,
        name: str,
        unit: str,
        metadata: dict[str, Any] | None = None,
    ) -> ChannelRecord:
        result = await self.session.execute(
            select(ChannelRecord).where(
                ChannelRecord.device_id == device_id,
                ChannelRecord.name == name,
            )
        )

        channel = result.scalar_one_or_none()

        if channel is not None:
            return channel

        channel = ChannelRecord(
            device_id=device_id,
            name=name,
            unit=unit,
            metadata_=metadata or {},
        )

        self.session.add(channel)
        await self.session.flush()

        return channel


class MeasurementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(
        self,
        measurement: Measurement,
    ) -> MeasurementRecord:
        record = measurement_to_record(measurement)

        self.session.add(record)
        await self.session.flush()

        return record

    async def list(
        self,
        *,
        device_id: str | None = None,
        channel: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Measurement]:
        statement = select(MeasurementRecord)

        if device_id is not None:
            statement = statement.where(MeasurementRecord.device_id == device_id)

        if channel is not None:
            statement = statement.where(MeasurementRecord.channel == channel)

        if start is not None:
            statement = statement.where(MeasurementRecord.timestamp >= start)

        if end is not None:
            statement = statement.where(MeasurementRecord.timestamp <= end)

        statement = (
            statement.order_by(MeasurementRecord.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return [record_to_measurement(record) for record in result.scalars().all()]


class SpectrumRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(
        self,
        spectrum: Spectrum,
    ) -> SpectrumRecord:
        record = spectrum_to_record(spectrum)

        self.session.add(record)
        await self.session.flush()

        return record

    async def list(
        self,
        *,
        device_id: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Spectrum]:
        statement = select(SpectrumRecord)

        if device_id is not None:
            statement = statement.where(SpectrumRecord.device_id == device_id)

        if start is not None:
            statement = statement.where(SpectrumRecord.timestamp >= start)

        if end is not None:
            statement = statement.where(SpectrumRecord.timestamp <= end)

        statement = (
            statement.order_by(SpectrumRecord.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return [record_to_spectrum(record) for record in result.scalars().all()]


class ExperimentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        name: str,
        description: str | None,
        metadata: dict[str, Any],
    ) -> ExperimentRecord:
        experiment = ExperimentRecord(
            name=name,
            description=description,
            metadata_=metadata,
        )

        self.session.add(experiment)
        await self.session.flush()

        return experiment

    async def list(self) -> list[ExperimentRecord]:
        result = await self.session.execute(
            select(ExperimentRecord).order_by(ExperimentRecord.created_at.desc())
        )

        return list(result.scalars().all())
