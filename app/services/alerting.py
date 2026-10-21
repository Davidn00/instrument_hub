"""Persistence and notification orchestration for alert events."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.measurement import Measurement
from app.services.alert_engine import evaluate_rule
from app.storage.models import AlertRecord, AlertRuleRecord


class AlertingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def evaluate_measurement(
        self,
        measurement: Measurement,
    ) -> list[dict[str, Any]]:
        """Evaluate enabled rules and persist newly triggered events."""

        result = await self.session.execute(
            select(AlertRuleRecord).where(AlertRuleRecord.enabled.is_(True))
        )
        rules = list(result.scalars().all())

        notifications: list[dict[str, Any]] = []

        for rule in rules:
            payload = evaluate_rule(rule, measurement)
            if payload is None:
                continue

            # A rule/device/channel event stays active while the threshold
            # remains violated. Do not create a new record for every sample.
            active_result = await self.session.execute(
                select(AlertRecord)
                .where(
                    AlertRecord.device_id == measurement.device_id,
                    AlertRecord.channel == measurement.channel,
                    AlertRecord.acknowledged.is_(False),
                    AlertRecord.metadata_["rule_id"].astext == str(rule.id),
                )
                .order_by(AlertRecord.timestamp.desc())
                .limit(1)
            )
            active_alert = active_result.scalar_one_or_none()

            if active_alert is not None:
                continue

            record = AlertRecord(
                timestamp=datetime.now(UTC),
                device_id=measurement.device_id,
                channel=measurement.channel,
                severity=rule.severity,
                message=payload["message"],
                value=payload["value"],
                acknowledged=False,
                metadata_={
                    **payload,
                    "unit": measurement.unit,
                    "measurement_timestamp": measurement.timestamp.isoformat(),
                },
            )
            self.session.add(record)
            await self.session.flush()

            payload["id"] = str(record.id)
            payload["timestamp"] = record.timestamp.isoformat()
            payload["acknowledged"] = False
            notifications.append(payload)

        return notifications
