from __future__ import annotations

from typing import Any

from fastapi import WebSocket


class WebSocketManager:
    """Manages active WebSocket clients."""

    def __init__(
        self,
        max_connections: int = 100,
    ) -> None:
        self.max_connections = max_connections
        self._connections: set[WebSocket] = set()

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    async def connect(
        self,
        websocket: WebSocket,
    ) -> bool:
        if len(self._connections) >= self.max_connections:
            await websocket.close(
                code=1013,
                reason="Maximum WebSocket connections reached.",
            )
            return False

        await websocket.accept()
        self._connections.add(websocket)

        return True

    def disconnect(
        self,
        websocket: WebSocket,
    ) -> None:
        self._connections.discard(websocket)

    async def broadcast(
        self,
        message: dict[str, Any],
    ) -> None:
        disconnected: list[WebSocket] = []

        for websocket in self._connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)
