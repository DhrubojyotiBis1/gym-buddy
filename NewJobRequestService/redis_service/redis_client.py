from redis_service.redis_connector import RedisConnector
from config import Config
import redis.asyncio as redis
import json


class RedisClient:
    def __init__(self, connector: RedisConnector):
        self.client = redis.Redis(connection_pool=connector.pool)
    
    async def add(self, key: str, value: str, ex: int):
        await self.client.set(key, value, ex=ex)
        return True

    async def update(self, key: str, value: str):
        if await self.client.exists(key):
            ttl = await self.client.ttl(key)
            if ttl > 0:
                await self.client.set(key, value, ex=ttl)
            else:
                await self.client.set(key, value)
            return True
        return False

    async def get_all(self):
        set_key = f"*-{Config.REDIS_DETAILS_KEY}"
        result = []
        
        async for key in self.client.scan_iter(match=set_key):
            job_data = await self.get(key)
            result.append(job_data)
        return result

    async def get(self, key: str):
        value = await self.client.get(key)
        if value is None:
            return {}
        return {'id': key, 'job_details': json.loads(value)}

    async def delete(self, key: str):
        deleted = await self.client.delete(key)
        return deleted > 0

connector = RedisConnector()
        
async def get_redis_client() -> RedisClient:
    return RedisClient(connector)

async def close_redis_connection():
    await connector.close()