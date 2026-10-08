from datetime import datetime

import numpy as np
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.storage import (
    SpectrumCreate,
    SpectrumResponse,
)
from app.models.spectrum import Spectrum
from app.storage.db import get_db
from app.storage.repositories import SpectrumRepository

router = APIRouter(
    prefix="/spectra",
)


@router.get(
    "",
    response_model=list[SpectrumResponse],
)
async def list_spectra(
    device_id: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    session: AsyncSession = Depends(get_db),
) -> list[SpectrumResponse]:
    repository = SpectrumRepository(session)

    spectra = await repository.list(
        device_id=device_id,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )

    return [
        SpectrumResponse(
            timestamp=spectrum.timestamp,
            device_id=spectrum.device_id,
            wavelength=spectrum.wavelength.tolist(),
            intensity=spectrum.intensity.tolist(),
            wavelength_unit=spectrum.wavelength_unit,
            intensity_unit=spectrum.intensity_unit,
            metadata=spectrum.metadata,
        )
        for spectrum in spectra
    ]


@router.post(
    "",
    response_model=SpectrumResponse,
    status_code=201,
)
async def create_spectrum(
    request: SpectrumCreate,
    session: AsyncSession = Depends(get_db),
) -> SpectrumResponse:
    spectrum = Spectrum(
        timestamp=request.timestamp,
        device_id=request.device_id,
        wavelength=np.asarray(request.wavelength, dtype=float),
        intensity=np.asarray(request.intensity, dtype=float),
        wavelength_unit=request.wavelength_unit,
        intensity_unit=request.intensity_unit,
        metadata=request.metadata,
    )

    repository = SpectrumRepository(session)

    record = await repository.add(spectrum)

    await session.commit()

    return SpectrumResponse(
        id=record.id,
        timestamp=spectrum.timestamp,
        device_id=spectrum.device_id,
        wavelength=spectrum.wavelength.tolist(),
        intensity=spectrum.intensity.tolist(),
        wavelength_unit=spectrum.wavelength_unit,
        intensity_unit=spectrum.intensity_unit,
        metadata=spectrum.metadata,
    )
