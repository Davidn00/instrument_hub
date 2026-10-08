from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.storage import MeasurementResponse
from app.storage.db import get_db
from app.storage.repositories import MeasurementRepository

router = APIRouter(
    prefix="/measurements",
)


@router.get(
    "",
    response_model=list[MeasurementResponse],
)
async def list_measurements(
    device_id: str | None = None,
    channel: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=5000,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    session: AsyncSession = Depends(get_db),
) -> list[MeasurementResponse]:
    repository = MeasurementRepository(session)

    measurements = await repository.list(
        device_id=device_id,
        channel=channel,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )

    return [
        MeasurementResponse(
            timestamp=measurement.timestamp,
            device_id=measurement.device_id,
            channel=measurement.channel,
            value=measurement.value,
            unit=measurement.unit,
            quality=measurement.quality,
            metadata=measurement.metadata,
        )
        for measurement in measurements
    ]
