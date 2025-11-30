from abc import ABC, abstractmethod
from services.redis.redis_connector_interface import IRedisConnector

class IRedisRepository(ABC):
    @abstractmethod
    async def get_participants(self, redis_connector: IRedisConnector, conversation_id: str):
        """
        Fetches the participants of a conversation from Redis.
        """
        pass

    @abstractmethod
    async def get_service_for(self, redis_connector: IRedisConnector, receiver_email: str):
        """
        Fetches the service associated with a receiver from Redis.
        """
        pass
