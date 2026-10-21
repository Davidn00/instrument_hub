"""Request and response schemas for alert rules and alert events."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AlertRuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    metric: Literal[
        "temperature",
        "strain",
        "wavelength_drift",
        "signal_quality",
    ]
    operator: Literal["gt", "gte", "lt", "lte"]
    threshold: float
    device_id: str | None = None
    channel: str | None = None
    severity: Literal["INFO", "WARNING", "CRITICAL"] = "WARNING"
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class AlertRuleResponse(AlertRuleCreate):
    id: UUID
    created_at: datetime


class AlertResponse(BaseModel):
    id: UUID
    timestamp: datetime
    device_id: str
    channel: str | None
    severity: str
    message: str
    value: float | None
    acknowledged: bool
    metadata: dict[str, Any]


class AlertAcknowledgeRequest(BaseModel):
    acknowledged: bool = True
