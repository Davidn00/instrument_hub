"""REST endpoints for alert rules and alert history."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.alerts import (
    AlertAcknowledgeRequest,
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
)
from app.storage.db import get_db
from app.storage.models import AlertRecord, AlertRuleRecord

router = APIRouter(prefix="/alerts")


def alert_response(record: AlertRecord) -> AlertResponse:
    """Convert an ORM alert to its public response schema."""

    return AlertResponse(
        id=record.id,
        timestamp=record.timestamp,
        device_id=record.device_id,
        channel=record.channel,
        severity=record.severity,
        message=record.message,
        value=record.value,
        acknowledged=record.acknowledged,
        metadata=record.metadata_,
    )


def rule_response(record: AlertRuleRecord) -> AlertRuleResponse:
    """Convert an ORM rule to its public response schema."""

    return AlertRuleResponse.model_validate(
        {
            "id": record.id,
            "name": record.name,
            "metric": record.metric,
            "operator": record.operator,
            "threshold": record.threshold,
            "device_id": record.device_id,
            "channel": record.channel,
            "severity": record.severity,
            "enabled": record.enabled,
            "metadata": record.metadata_,
            "created_at": record.created_at,
        }
    )


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    active_only: bool = False,
    limit: int = Query(default=100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
) -> list[AlertResponse]:
    """Return the most recent alerts."""

    statement = select(AlertRecord).order_by(AlertRecord.timestamp.desc()).limit(limit)

    if active_only:
        statement = statement.where(AlertRecord.acknowledged.is_(False))

    result = await session.execute(statement)
    return [alert_response(item) for item in result.scalars().all()]


@router.post(
    "/rules",
    response_model=AlertRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_alert_rule(
    request: AlertRuleCreate,
    session: AsyncSession = Depends(get_db),
) -> AlertRuleResponse:
    """Create a configurable threshold rule."""

    if request.device_id:
        from app.storage.models import DeviceRecord

        device = await session.execute(
            select(DeviceRecord).where(DeviceRecord.device_id == request.device_id)
        )
        if device.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=422,
                detail="The selected device does not exist.",
            )

    record = AlertRuleRecord(
        name=request.name.strip(),
        metric=request.metric,
        operator=request.operator,
        threshold=request.threshold,
        device_id=request.device_id,
        channel=request.channel,
        severity=request.severity,
        enabled=request.enabled,
        metadata_=request.metadata,
    )

    if not record.name:
        raise HTTPException(
            status_code=422,
            detail="Rule name cannot be empty.",
        )

    session.add(record)
    await session.commit()
    await session.refresh(record)
    return rule_response(record)


@router.get("/rules", response_model=list[AlertRuleResponse])
async def list_alert_rules(
    session: AsyncSession = Depends(get_db),
) -> list[AlertRuleResponse]:
    """List all configured rules, including disabled rules."""

    result = await session.execute(
        select(AlertRuleRecord).order_by(AlertRuleRecord.created_at.desc())
    )
    return [rule_response(item) for item in result.scalars().all()]


@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: UUID,
    request: AlertAcknowledgeRequest,
    session: AsyncSession = Depends(get_db),
) -> AlertResponse:
    """Acknowledge or reopen an alert event."""

    result = await session.execute(
        select(AlertRecord).where(AlertRecord.id == alert_id)
    )
    record = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(status_code=404, detail="Alert not found.")

    record.acknowledged = request.acknowledged
    metadata: dict[str, Any] = dict(record.metadata_)
    metadata["acknowledged_at"] = (
        datetime.now(UTC).isoformat() if request.acknowledged else None
    )
    record.metadata_ = metadata

    await session.commit()
    await session.refresh(record)
    return alert_response(record)
