from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.storage import (
    DeviceCreate,
    DeviceResponse,
)
from app.storage.db import get_db
from app.storage.repositories import (
    ChannelRepository,
    DeviceRepository,
)

router = APIRouter(
    prefix="/devices",
)


@router.get(
    "",
    response_model=list[DeviceResponse],
)
async def list_devices(
    session: AsyncSession = Depends(get_db),
) -> list[DeviceResponse]:
    repository = DeviceRepository(session)

    devices = await repository.list()

    return [
        DeviceResponse(
            id=device.id,
            device_id=device.device_id,
            name=device.name,
            device_type=device.device_type,
            interface=device.interface,
            status=device.status,
            metadata=device.metadata_,
        )
        for device in devices
    ]


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_device(
    request: DeviceCreate,
    session: AsyncSession = Depends(get_db),
) -> DeviceResponse:
    repository = DeviceRepository(session)

    existing = await repository.get_by_device_id(request.device_id)

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(f"Device '{request.device_id}' already exists."),
        )

    device = await repository.create(
        device_id=request.device_id,
        name=request.name,
        device_type=request.device_type,
        interface=request.interface,
        metadata=request.metadata,
    )

    channel_repository = ChannelRepository(session)

    for channel in request.channels:
        await channel_repository.get_or_create(
            device_id=request.device_id,
            name=channel.name,
            unit=channel.unit,
            metadata=channel.metadata,
        )

    await session.commit()

    return DeviceResponse(
        id=device.id,
        device_id=device.device_id,
        name=device.name,
        device_type=device.device_type,
        interface=device.interface,
        status=device.status,
        metadata=device.metadata_,
    )
