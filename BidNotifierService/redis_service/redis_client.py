from redis_service.redis_connector import RedisConnector
import redis.asyncio as redis


class RedisClient:
    """
    Async Redis client wrapper with Pub/Sub support.
    Uses connection pooling for efficiency across app instances.
    """

    def __init__(self, connector: RedisConnector):
        self.client = redis.Redis(connection_pool=connector.pool)

    async def subscribe(self, channel: str):
        """
        Subscribes to a Redis Pub/Sub channel and returns a PubSub object.
        The returned PubSub can be used in async iteration for continuous listening.
        """
        try:
            pubsub = self.client.pubsub(ignore_subscribe_messages=True)
            await pubsub.subscribe(channel)
            return pubsub
        except Exception as e:
            raise RuntimeError(f"Failed to subscribe to channel '{channel}': {e}")

    async def unsubscribe(self, pubsub, channel: str):
        """
        Gracefully unsubscribes and closes the Pub/Sub connection.
        """
        if not pubsub:
            return
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
        except Exception as e:
            raise RuntimeError(f"Error closing Redis Pub/Sub for channel '{channel}': {e}")
    
    async def get(self, key: str):
        """
        Fetches a value from Redis by key.
        Automatically decodes bytes to UTF-8 strings.
        Returns None if key does not exist.
        """
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            return value
        except Exception as e:
            raise RuntimeError(f"Failed to get value for key '{key}': {e}")


# --- Singleton Redis Connector for FastAPI Dependency Injection ---

connector = RedisConnector()


async def get_redis_client() -> RedisClient:
    return RedisClient(connector)


async def close_redis_connection():
    await connector.close()
