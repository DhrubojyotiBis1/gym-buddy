from services.direct_chat_gprc.direct_chat_connector import DirectChatClientConnector
from services.direct_chat_gprc.connection_manager_interface import IConnectionManager
from typing import Dict
import asyncio

class DirectChatConnectionManager(IConnectionManager):
    _instance = None
    _instance_lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_singleton_lock"):
            cls._singleton_lock = asyncio.Lock()
        if cls._instance is None:
            cls._instance = super(DirectChatConnectionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Only initialize once
        if getattr(self, "_initialized", False):
            return
        self._connectors: Dict[str, DirectChatClientConnector] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._initialized = True

    async def get_connector(self, host: str, port: str) -> DirectChatClientConnector:
        # If there's already a connector for this port, reuse it
        chat_service = f'{host}:{port}'
        if port in self._connectors and self._connectors[chat_service].channel is not None:
            return self._connectors[chat_service]
        
        # Use a per-port lock to avoid race conditions
        if chat_service not in self._locks:
            self._locks[chat_service] = asyncio.Lock()

        async with self._locks[chat_service]:
            # Double check under the lock
            if chat_service in self._connectors and self._connectors[chat_service].channel is not None:
                return self._connectors[chat_service]

            connector = DirectChatClientConnector(host=host, port=port)
            await connector.connect()
            self._connectors[chat_service] = connector
            return connector

    async def close_connector(self, host: str, port: str):
        chat_service = f'{host}:{port}'
        connector = self._connectors.get(chat_service)
        if connector and connector.channel is not None:
            await connector.close()
        self._connectors.pop(port, None)
        self._locks.pop(port, None)

    async def close_all(self):
        for connector in list(self._connectors.values()):
            if connector.channel is not None:
                await connector.close()
        self._connectors.clear()
        self._locks.clear()

# Singleton Instance
connection_manager = DirectChatConnectionManager()
