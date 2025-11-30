from redis_service.redis_connector import RedisConnector
import redis.asyncio as redis
from logger import get_logger

logger = get_logger()


class RedisClient:
    def __init__(self, connector: RedisConnector):
        self.client = redis.Redis(connection_pool=connector.pool)

    async def put_in_set(self, key: str, value: str) -> None:
        logger.debug(f"Adding '{value}' to set '{key}'")
        await self.client.sadd(key, value)
        logger.info(f"Added '{value}' to set '{key}'")

    async def get_from_set(self, key: str) -> list[str]:
        logger.debug(f"Fetching all members from set '{key}'")
        members = await self.client.smembers(key)
        results = []
        for m in members:
            if isinstance(m, bytes):
                results.append(m.decode())
            else:
                results.append(m)
        logger.info(f"Fetched {len(results)} members from set '{key}'")
        return results

    async def put_in_hash(self, hash_key: str, mapping: dict) -> None:
        logger.debug(f"Setting fields in hash '{hash_key}': {list(mapping.keys())}")
        await self.client.hset(hash_key, mapping=mapping)
        logger.info(f"Set fields in hash '{hash_key}': {list(mapping.keys())}")

    async def get_from_hash(self, hash_key: str, fields: list[str]) -> dict:
        logger.debug(f"Getting fields {fields} from hash '{hash_key}'")
        values = await self.client.hmget(hash_key, fields)
        result = {}
        for field, value in zip(fields, values):
            if value is None:
                result[field] = None
            elif isinstance(value, bytes):
                result[field] = value.decode()
            else:
                result[field] = value
        logger.info(f"Fetched fields from hash '{hash_key}': {fields}")
        return result

    async def put(self, key: str, value: str) -> None:
        logger.debug(f"Setting '{key}' = '{value}'")
        await self.client.set(key, value)
        logger.info(f"Set '{key}' in Redis")

    async def get(self, key: str) -> str | None:
        logger.debug(f"Fetching value for key '{key}'")
        value = await self.client.get(key)
        if value is None:
            logger.info(f"Key '{key}' not found")
            return None
        if isinstance(value, bytes):
            value = value.decode()
        logger.info(f"Fetched key '{key}' from Redis")
        return value

    async def remove(self, key: str) -> None:
        logger.debug(f"Deleting key '{key}'")
        await self.client.delete(key)
        logger.info(f"Deleted key '{key}' from Redis")


# Global RedisConnector instance
_connector = RedisConnector()

async def get_redis_client() -> RedisClient:
    logger.info("Creating a new RedisClient instance")
    return RedisClient(_connector)

async def close_redis_connection():
    logger.info("Closing RedisConnector connection pool")
    await _connector.close()