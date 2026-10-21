from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.storage import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentResultCreate,
    ExperimentStatusUpdate,
)
from app.services.experiments import ExperimentService
from app.storage.db import get_db
from app.storage.models import ExperimentRecord

router = APIRouter(prefix="/experiments")


def to_response(experiment: ExperimentRecord) -> ExperimentResponse:
    """Map the persistence model to the existing public API schema."""

    return ExperimentResponse(
        id=experiment.id,
        name=experiment.name,
        description=experiment.description,
        status=experiment.status,
        started_at=experiment.started_at,
        ended_at=experiment.ended_at,
        metadata=experiment.metadata_,
    )


@router.get("", response_model=list[ExperimentResponse])
async def list_experiments(
    session: AsyncSession = Depends(get_db),
) -> list[ExperimentResponse]:
    service = ExperimentService(session)
    return [to_response(item) for item in await service.list()]


@router.post(
    "",
    response_model=ExperimentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_experiment(
    request: ExperimentCreate,
    session: AsyncSession = Depends(get_db),
) -> ExperimentResponse:
    service = ExperimentService(session)

    try:
        experiment = await service.create(
            name=request.name,
            description=request.description,
            configuration=request.configuration.model_dump(mode="json"),
            metadata=request.metadata,
        )
        await session.commit()
        return to_response(experiment)
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> ExperimentResponse:
    service = ExperimentService(session)
    experiment = await service.get(experiment_id)

    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found.")

    return to_response(experiment)


@router.patch(
    "/{experiment_id}/status",
    response_model=ExperimentResponse,
)
async def update_experiment_status(
    experiment_id: UUID,
    request: ExperimentStatusUpdate,
    session: AsyncSession = Depends(get_db),
) -> ExperimentResponse:
    service = ExperimentService(session)
    experiment = await service.get(experiment_id)

    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found.")

    try:
        await service.transition(experiment, request.status)
        await session.commit()
        return to_response(experiment)
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/{experiment_id}/results",
    response_model=ExperimentResponse,
)
async def add_experiment_result(
    experiment_id: UUID,
    request: ExperimentResultCreate,
    session: AsyncSession = Depends(get_db),
) -> ExperimentResponse:
    service = ExperimentService(session)
    experiment = await service.get(experiment_id)

    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found.")

    try:
        await service.add_result(
            experiment,
            result_type=request.result_type,
            data=request.data,
            summary=request.summary,
        )
        await session.commit()
        return to_response(experiment)
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
