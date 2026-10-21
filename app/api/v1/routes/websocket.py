from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.runtime import websocket_manager

router = APIRouter()


@router.websocket("/ws/measurements")
async def measurements_websocket(
    websocket: WebSocket,
) -> None:
    connected = await websocket_manager.connect(websocket)

    if not connected:
        return

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

    except Exception:
        websocket_manager.disconnect(websocket)


@router.websocket("/ws/notifications")
async def notifications_websocket(
    websocket: WebSocket,
) -> None:
    """Stream alert and dashboard notification events."""

    connected = await websocket_manager.connect(websocket)

    if not connected:
        return

    try:
        # Keep the connection alive while the server broadcasts events.
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

    except Exception:
        websocket_manager.disconnect(websocket)
