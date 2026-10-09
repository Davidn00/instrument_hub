import pytest

from app.realtime.websocket import WebSocketManager


class FakeWebSocket:
    def __init__(self) -> None:
        self.accepted = False
        self.messages: list[dict] = []

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(
        self,
        message: dict,
    ) -> None:
        self.messages.append(message)

    async def close(
        self,
        code: int,
        reason: str,
    ) -> None:
        return None


@pytest.mark.asyncio
async def test_websocket_manager_accepts_connection() -> None:
    manager = WebSocketManager(max_connections=2)

    websocket = FakeWebSocket()

    connected = await manager.connect(websocket)

    assert connected is True
    assert websocket.accepted is True
    assert manager.connection_count == 1


@pytest.mark.asyncio
async def test_websocket_manager_broadcasts_message() -> None:
    manager = WebSocketManager(max_connections=2)

    websocket = FakeWebSocket()

    await manager.connect(websocket)

    message = {
        "type": "measurement",
        "data": {
            "value": 10.0,
        },
    }

    await manager.broadcast(message)

    assert websocket.messages == [message]


@pytest.mark.asyncio
async def test_websocket_manager_disconnects() -> None:
    manager = WebSocketManager(max_connections=2)

    websocket = FakeWebSocket()

    await manager.connect(websocket)

    manager.disconnect(websocket)

    assert manager.connection_count == 0
