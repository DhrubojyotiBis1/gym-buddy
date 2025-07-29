from repositories.redis_interface import IRedisRepository
from redis_service.redis_client import RedisClient
from schemas.new_job_request import JobRequest
from datetime import datetime
from config import Config

class RedisRepository(IRedisRepository):
    async def insert(self, id: str, job_data: JobRequest, redis: RedisClient, expire_in: int):
        key = f'{id}:{datetime.now()}-{Config.REDIS_DETAILS_KEY}'
        return await redis.add(key, job_data.model_dump_json(), expire_in)
    
    async def get_all(self, redis: RedisClient):
        return await redis.get_all()
    
    async def get_by_id(self, id: str, redis: RedisClient):
        return await redis.get(id)
    