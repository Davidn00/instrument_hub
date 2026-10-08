from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.storage import (
    ExperimentCreate,
    ExperimentResponse,
)
from app.storage.db import get_db
from app.storage.repositories import ExperimentRepository

router = APIRouter(
    prefix="/experiments",
)


@router.get(
    "",
    response_model=list[ExperimentResponse],
)
async def list_experiments(
    session: AsyncSession = Depends(get_db),
) -> list[ExperimentResponse]:
    repository = ExperimentRepository(session)

    experiments = await repository.list()

    return [
        ExperimentResponse(
            id=experiment.id,
            name=experiment.name,
            description=experiment.description,
            status=experiment.status,
            started_at=experiment.started_at,
            ended_at=experiment.ended_at,
            metadata=experiment.metadata_,
        )
        for experiment in experiments
    ]


@router.post(
    "",
    response_model=ExperimentResponse,
    status_code=201,
)
async def create_experiment(
    request: ExperimentCreate,
    session: AsyncSession = Depends(get_db),
) -> ExperimentResponse:
    repository = ExperimentRepository(session)

    experiment = await repository.create(
        name=request.name,
        description=request.description,
        metadata=request.metadata,
    )

    await session.commit()

    return ExperimentResponse(
        id=experiment.id,
        name=experiment.name,
        description=experiment.description,
        status=experiment.status,
        started_at=experiment.started_at,
        ended_at=experiment.ended_at,
        metadata=experiment.metadata_,
    )
