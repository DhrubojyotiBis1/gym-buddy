from abc import ABC, abstractmethod
from fastapi import WebSocket

class IWebsocketConnectionManager(ABC):
    @abstractmethod
    async def connect(self, user_id: str, websocket: WebSocket): pass

    @abstractmethod
    async def disconnect(self, user_id: str): pass

    @abstractmethod
    async def send_message_to_user(self, message: str, user_id: str): pass