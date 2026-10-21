"""Notification delivery adapters for dashboard, WebSocket and email."""

import asyncio
import logging
import smtplib
from email.message import EmailMessage
from typing import Any

from app.core.config import get_settings
from app.realtime.websocket import WebSocketManager

logger = logging.getLogger(__name__)


class NotificationService:
    """Deliver alert events to connected clients and optional email."""

    def __init__(self, websocket_manager: WebSocketManager) -> None:
        self.websocket_manager = websocket_manager
        self.settings = get_settings()

    async def publish_alert(self, alert: dict[str, Any]) -> None:
        """Broadcast the event to all currently connected WebSocket clients."""

        # A dedicated event type keeps measurement and spectrum consumers intact.
        await self.websocket_manager.broadcast(
            {
                "type": "alert",
                "data": alert,
            }
        )

        # Email is optional; missing SMTP configuration must not stop acquisition.
        if not (
            self.settings.smtp_host
            and self.settings.smtp_from_email
            and self.settings.alert_email_to
        ):
            return

        try:
            await asyncio.to_thread(self._send_email, alert)
        except Exception:
            # Log delivery failures without logging passwords or message secrets.
            logger.exception("Could not deliver InstrumentHub alert email.")

    def _send_email(self, alert: dict[str, Any]) -> None:
        """Perform blocking SMTP I/O in a worker thread."""

        host = self.settings.smtp_host
        if host is None:
            raise RuntimeError("SMTP host is not configured.")

        message = EmailMessage()
        message["Subject"] = f"[InstrumentHub] {alert.get('severity', 'WARNING')} alert"
        message["From"] = self.settings.smtp_from_email
        message["To"] = self.settings.alert_email_to
        message.set_content(
            "\n".join(
                [
                    "InstrumentHub generated an alert.",
                    "",
                    f"Message: {alert.get('message', 'Alert triggered')}",
                    f"Device: {alert.get('device_id', 'Unknown')}",
                    f"Channel: {alert.get('channel', 'Unknown')}",
                    f"Value: {alert.get('value', 'Unavailable')}",
                    f"Severity: {alert.get('severity', 'WARNING')}",
                    f"Timestamp: {alert.get('timestamp', 'Unknown')}",
                ]
            )
        )

        with smtplib.SMTP(
            host,
            self.settings.smtp_port,
            timeout=10,
        ) as smtp:
            smtp.ehlo()

            if self.settings.smtp_starttls:
                smtp.starttls()
                smtp.ehlo()

            if self.settings.smtp_username:
                smtp.login(
                    self.settings.smtp_username,
                    self.settings.smtp_password or "",
                )

            smtp.send_message(message)
