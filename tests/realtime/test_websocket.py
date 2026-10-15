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


@pytest.mark.asyncio
async def test_websocket_manager_broadcasts_spectrum() -> None:
    manager = WebSocketManager(max_connections=2)
    websocket = FakeWebSocket()

    await manager.connect(websocket)

    event = {
        "type": "spectrum",
        "data": {
            "device_id": "fbg-live-001",
            "timestamp": "2026-10-15T12:00:00+00:00",
            "wavelength": [1549.0, 1550.0, 1551.0],
            "intensity": [0.1, 1.0, 0.2],
            "wavelength_unit": "nm",
            "intensity_unit": "a.u.",
            "metadata": {},
        },
    }

    await manager.broadcast(event)

    assert websocket.messages == [event]
    assert websocket.messages[0]["type"] == "spectrum"
    assert len(websocket.messages[0]["data"]["wavelength"]) == 3
    assert len(websocket.messages[0]["data"]["intensity"]) == 3
