from app.core.config import get_settings
from app.realtime.websocket import WebSocketManager
from app.services.acquisition import AcquisitionService
from app.storage.db import AsyncSessionFactory

settings = get_settings()


websocket_manager = WebSocketManager(
    max_connections=settings.websocket_max_connections,
)


acquisition_service = AcquisitionService(
    session_factory=AsyncSessionFactory,
    websocket_manager=websocket_manager,
)
