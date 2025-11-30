from abc import ABC, abstractmethod
from services.direct_chat_gprc.direct_chat_connector import DirectChatClientConnector

class IConnectionManager(ABC):
    @abstractmethod
    async def get_connector(self, host: str, port: str) -> DirectChatClientConnector:
        """
        Get or establish a connector for the specified host and port.

        Args:
            host (str): The host to connect to.
            port (str): The port string to connect to.

        Returns:
            DirectChatClientConnector: An established connector for the given host and port.
        """
        pass

    @abstractmethod
    async def close_connector(self, host: str, port: str):
        """
        Close the connector for the specified host and port.

        Args:
            host (str): The host whose connector should be closed.
            port (str): The port string to close the connector for.
        """
        pass

    @abstractmethod
    async def close_all(self):
        """
        Close all active connectors and clear all internal state.
        """
        pass
