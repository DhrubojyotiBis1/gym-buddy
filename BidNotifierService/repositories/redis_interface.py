from abc import ABC, abstractmethod
from redis_service.redis_client import RedisClient

class IRedisRepository(ABC):

    @abstractmethod
    def subscribe(self, job_id: str, redis: RedisClient): pass

    @abstractmethod
    def subscribe(self, job_id: str, redis: RedisClient): pass

    @abstractmethod
    def get_message(self) -> str | None: pass

    @abstractmethod
    def get_existing_bids(self, job_id: str, redis: RedisClient) -> str | None: pass