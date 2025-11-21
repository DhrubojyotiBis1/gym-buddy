from redis_service.redis_connector import RedisConnector
import redis.asyncio as redis
from logger import get_logger

# TODO: Add exception handling

logger = get_logger()

class RedisClient:
    def __init__(self, connector: RedisConnector):
        self.client = redis.Redis(connection_pool=connector.pool)

    async def put_in_set(self, key: str, value: str) -> None:
        """
        Adds a value to a Redis set at the given key.
        """
        logger.debug(f"Adding value '{value}' to set '{key}' in Redis.")
        await self.client.sadd(key, value)
        logger.info(f"Added value '{value}' to set '{key}' in Redis.")

    async def get_from_set(self, key: str) -> list[str]:
        """
        Gets all values from the Redis set at the given key.
        Returns a list of string values.
        """
        logger.debug(f"Getting members from set '{key}' in Redis.")
        members = await self.client.smembers(key)
        # Redis client returns set of bytes; decode to string if necessary
        if members and isinstance(next(iter(members), None), bytes):
            decoded_members = [member.decode() for member in members]
            logger.info(f"Fetched {len(decoded_members)} members from set '{key}' in Redis.")
            return decoded_members
        logger.info(f"Fetched {len(members)} members from set '{key}' in Redis.")
        return list(members)

    async def put(self, key: str, value: str) -> None:
        """
        Stores a string value by key in Redis.
        """
        logger.debug(f"Storing key '{key}' with value '{value}' in Redis.")
        await self.client.set(key, value)
        logger.info(f"Stored key '{key}' with value in Redis.")

    async def get(self, key: str) -> str | None:
        """
        Gets a string value by key from Redis. Returns None if not found.
        """
        logger.debug(f"Getting value for key '{key}' from Redis.")
        value = await self.client.get(key)
        if value is None:
            logger.info(f"Key '{key}' not found in Redis.")
            return None
        # Redis client may return bytes; decode to string if necessary
        if isinstance(value, bytes):
            decoded_value = value.decode()
            logger.info(f"Fetched key '{key}' from Redis with value.")
            return decoded_value
        logger.info(f"Fetched key '{key}' from Redis with value.")
        return value

    async def remove(self, key: str) -> None:
        """
        Removes the key and its associated value from Redis.
        """
        logger.debug(f"Removing key '{key}' from Redis.")
        await self.client.delete(key)
        logger.info(f"Removed key '{key}' from Redis.")


connector = RedisConnector()

async def get_redis_client() -> RedisClient:
    logger.info("Providing new RedisClient instance")
    return RedisClient(connector)

async def close_redis_connection():
    logger.info("Closing global RedisConnector")
    await connector.close()