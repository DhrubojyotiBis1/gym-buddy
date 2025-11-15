from fastapi import WebSocket
from typing import Dict
from connection_services.websocket.websocket_connection_manager_interface import IWebsocketConnectionManager
import asyncio

class WebsocketConnectionManager(IWebsocketConnectionManager):
    """
    Singleton class that manages active websocket connections in a thread-safe manner.
    """
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WebsocketConnectionManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.active_connections: Dict[str, WebSocket] = {}
        self._connections_lock = asyncio.Lock()
        self._initialized = True

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self._connections_lock:
            self.active_connections[user_id] = websocket

    async def disconnect(self, user_id: str):
        async with self._connections_lock:
            if user_id in self.active_connections:
                self.active_connections.pop(user_id)

    async def send_message_to_user(self, message: str, user_id: str):
        async with self._connections_lock:
            websocket = self.active_connections.get(user_id)
        if websocket:
            try:
                await websocket.send_text(message)
            except Exception:
                pass  # (In prod you might want to log failures.)