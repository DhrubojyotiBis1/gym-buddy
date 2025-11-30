from services.redis.redis_connector import RedisConnector
import redis.asyncio as redis
from logger import get_logger

# TODO: Add exception handling

logger = get_logger()

class RedisClient:
    @staticmethod
    async def put_in_set(connector: RedisConnector, key: str, value: str) -> None:
        """
        Adds a value to a Redis set at the given key.
        """
        client = redis.Redis(connection_pool=connector.pool)
        logger.debug(f"Adding value '{value}' to set '{key}' in Redis.")
        await client.sadd(key, value)
        logger.info(f"Added value '{value}' to set '{key}' in Redis.")

    @staticmethod
    async def get_from_set(connector: RedisConnector, key: str) -> list[str]:
        """
        Gets all values from the Redis set at the given key.
        Returns a list of string values.
        """
        client = redis.Redis(connection_pool=connector.pool)
        logger.debug(f"Getting members from set '{key}' in Redis.")
        members = await client.smembers(key)
        # Redis client returns set of bytes; decode to string if necessary
        if members and isinstance(next(iter(members), None), bytes):
            decoded_members = [member.decode() for member in members]
            logger.info(f"Fetched {len(decoded_members)} members from set '{key}' in Redis.")
            return decoded_members
        logger.info(f"Fetched {len(members)} members from set '{key}' in Redis.")
        return list(members)
    
    @staticmethod
    async def get_from_hash(connector: RedisConnector, hash_key: str, fields: list[str] = ['host', 'port']) -> dict:
        """
        Gets the values of specific fields from a Redis hash by its key.
        Returns a dict mapping fields to their corresponding values (None if not found).

        Args:
            connector (RedisConnector): The Redis connector.
            hash_key (str): The key of the hash.
            fields (list[str]): List of field names to retrieve.

        Returns:
            dict: Dictionary of field-value pairs with values as strings or None where not found.
        """
        client = redis.Redis(connection_pool=connector.pool)
        logger.debug(f"Getting fields {fields} from hash '{hash_key}' in Redis.")
        values = await client.hmget(hash_key, fields)
        result = {}
        for field, value in zip(fields, values):
            if value is None:
                result[field] = None
            elif isinstance(value, bytes):
                result[field] = value.decode()
            else:
                result[field] = value
        logger.info(f"Fetched fields {fields} from hash '{hash_key}' in Redis.")
        return result

    @staticmethod
    async def put(connector: RedisConnector, key: str, value: str) -> None:
        """
        Stores a string value by key in Redis.
        """
        client = redis.Redis(connection_pool=connector.pool)
        logger.debug(f"Storing key '{key}' with value '{value}' in Redis.")
        await client.set(key, value)
        logger.info(f"Stored key '{key}' with value in Redis.")

    @staticmethod
    async def get(connector: RedisConnector, key: str) -> str | None:
        """
        Gets a string value by key from Redis. Returns None if not found.
        """
        client = redis.Redis(connection_pool=connector.pool)
        logger.debug(f"Getting value for key '{key}' from Redis.")
        value = await client.get(key)
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

    @staticmethod
    async def remove(connector: RedisConnector, key: str) -> None:
        """
        Removes the key and its associated value from Redis.
        """
        client = redis.Redis(connection_pool=connector.pool)
        logger.debug(f"Removing key '{key}' from Redis.")
        await client.delete(key)
        logger.info(f"Removed key '{key}' from Redis.")