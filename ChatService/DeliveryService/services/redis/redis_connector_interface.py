from abc import ABC, abstractmethod

class IRedisConnector(ABC):
    @abstractmethod
    async def close(self):
        """
        Closes the Redis connection pool or any associated resources.
        """
        pass
