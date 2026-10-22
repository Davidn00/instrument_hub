from typing import Any

import pytest

from app.api.v1.routes import websocket as websocket_routes
from app.realtime.websocket import WebSocketManager


class BroadcastingManager(WebSocketManager):
    """Publish one event as soon as a client connects."""

    async def connect(self, websocket: Any) -> bool:
        connected = await super().connect(websocket)

        if connected:
            await self.broadcast(
                {
                    "type": "test_event",
                    "data": {"value": 42},
                }
            )

        return connected


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/ws/measurements",
        "/api/v1/ws/notifications",
    ],
)
def test_websocket_routes_deliver_events_and_disconnect_cleanly(
    api_client,
    monkeypatch,
    path: str,
) -> None:
    manager = BroadcastingManager(max_connections=2)

    monkeypatch.setattr(
        websocket_routes,
        "websocket_manager",
        manager,
    )

    with api_client.websocket_connect(path) as websocket:
        event = websocket.receive_json()

        assert event == {
            "type": "test_event",
            "data": {"value": 42},
        }
        assert manager.connection_count == 1

    assert manager.connection_count == 0


def test_websocket_manager_removes_clients_that_fail_to_receive() -> None:
    import asyncio

    class BrokenWebSocket:
        async def accept(self) -> None:
            return None

        async def send_json(self, message: dict[str, Any]) -> None:
            raise RuntimeError("Simulated disconnected client")

        async def close(self, code: int, reason: str) -> None:
            return None

    async def scenario() -> None:
        manager = WebSocketManager(max_connections=2)
        websocket = BrokenWebSocket()

        assert await manager.connect(websocket) is True
        assert manager.connection_count == 1

        await manager.broadcast({"type": "measurement", "data": {}})

        assert manager.connection_count == 0

    asyncio.run(scenario())
