from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.storage import AcquisitionRequest
from app.services.runtime import acquisition_service
from app.storage.db import get_db
from app.storage.repositories import DeviceRepository

router = APIRouter(
    prefix="/acquisition",
)


@router.post("/start")
async def start_acquisition(
    request: AcquisitionRequest,
    session: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    repository = DeviceRepository(session)

    device = await repository.get_by_device_id(request.device_id)

    if device is None:
        raise HTTPException(
            status_code=404,
            detail=(f"Device '{request.device_id}' does not exist."),
        )

    if acquisition_service.is_running(request.device_id):
        return {
            "device_id": request.device_id,
            "status": "already_running",
        }

    try:
        await acquisition_service.start(device)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "device_id": request.device_id,
        "status": "started",
    }


@router.post("/stop")
async def stop_acquisition(
    request: AcquisitionRequest,
) -> dict[str, str]:
    await acquisition_service.stop(request.device_id)

    return {
        "device_id": request.device_id,
        "status": "stopped",
    }
