from abc import ABC, abstractmethod
from typing import Optional, Tuple
from schemas.bid import BidCreate
from redis_service.redis_client import RedisClient

class IRedisRepository(ABC):

    @abstractmethod
    def add_bid(self, bid: BidCreate, redis: RedisClient) -> bool: pass

    @abstractmethod
    def get(self, job_id: str, redis: RedisClient) -> dict: pass