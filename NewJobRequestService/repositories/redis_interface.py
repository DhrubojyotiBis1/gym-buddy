from abc import ABC, abstractmethod
from schemas.new_job_request import JobRequest
from redis_service.redis_client import RedisClient

class IRedisRepository(ABC):

    @abstractmethod
    def insert(self, id: str, job_data: JobRequest, redis: RedisClient, expire_in: int) -> bool: pass

    @abstractmethod
    def get_all(self, redis: RedisClient) -> dict: pass

    @abstractmethod
    def get_by_id(self, id: str, redis: RedisClient) -> dict: pass