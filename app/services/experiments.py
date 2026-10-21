"""Domain services for experiment lifecycle and result tracking."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.models import DeviceRecord, ExperimentRecord


class ExperimentService:
    """Coordinates experiment configuration, lifecycle and results."""

    VALID_TRANSITIONS = {
        "CREATED": {"RUNNING", "CANCELLED"},
        "RUNNING": {"COMPLETED", "FAILED", "CANCELLED"},
        "COMPLETED": set(),
        "FAILED": set(),
        "CANCELLED": set(),
    }

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        name: str,
        description: str | None,
        configuration: dict[str, Any],
        metadata: dict[str, Any],
    ) -> ExperimentRecord:
        """Validate referenced devices before persisting the experiment."""

        device_ids = configuration.get("device_ids", [])

        if not isinstance(device_ids, list):
            raise ValueError("configuration.device_ids must be a list.")

        if device_ids:
            result = await self.session.execute(
                select(DeviceRecord.device_id).where(
                    DeviceRecord.device_id.in_(device_ids)
                )
            )
            existing_ids = set(result.scalars().all())
            missing_ids = set(device_ids) - existing_ids

            if missing_ids:
                raise ValueError(
                    f"Unknown device IDs: {', '.join(sorted(missing_ids))}"
                )

        # Keep the configuration and results in the existing JSONB column.
        stored_metadata = dict(metadata)
        stored_metadata["configuration"] = configuration
        stored_metadata.setdefault("results", [])

        experiment = ExperimentRecord(
            name=name,
            description=description,
            metadata_=stored_metadata,
            status="CREATED",
        )

        self.session.add(experiment)
        await self.session.flush()
        return experiment

    async def get(self, experiment_id: UUID) -> ExperimentRecord | None:
        """Retrieve one experiment by its public identifier."""

        result = await self.session.execute(
            select(ExperimentRecord).where(ExperimentRecord.id == experiment_id)
        )
        return result.scalar_one_or_none()

    async def list(self) -> list[ExperimentRecord]:
        """Return experiments with the most recent first."""

        result = await self.session.execute(
            select(ExperimentRecord).order_by(ExperimentRecord.created_at.desc())
        )
        return list(result.scalars().all())

    async def transition(
        self,
        experiment: ExperimentRecord,
        new_status: str,
    ) -> ExperimentRecord:
        """Enforce valid lifecycle transitions."""

        allowed = self.VALID_TRANSITIONS.get(experiment.status, set())

        if new_status not in allowed:
            raise ValueError(
                f"Invalid experiment transition: {experiment.status} -> {new_status}"
            )

        now = datetime.now(UTC)

        experiment.status = new_status

        if new_status == "RUNNING":
            experiment.started_at = now

        if new_status in {"COMPLETED", "FAILED", "CANCELLED"}:
            experiment.ended_at = now

        await self.session.flush()
        return experiment

    async def add_result(
        self,
        experiment: ExperimentRecord,
        *,
        result_type: str,
        data: dict[str, Any],
        summary: str | None,
    ) -> ExperimentRecord:
        """Append a result without overwriting previous results."""

        if experiment.status not in {"RUNNING", "COMPLETED"}:
            raise ValueError(
                "Results can only be added to running or completed experiments."
            )

        # Copy nested containers to avoid mutating a shared JSON object in place.
        metadata = dict(experiment.metadata_)
        results = list(metadata.get("results", []))

        results.append(
            {
                "result_type": result_type,
                "data": data,
                "summary": summary,
                "created_at": datetime.now(UTC).isoformat(),
            }
        )

        metadata["results"] = results
        experiment.metadata_ = metadata

        await self.session.flush()
        return experiment
