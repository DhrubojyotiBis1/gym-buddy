import asyncio
import json
from redis_service.redis_client import RedisClient
from repositories.redis_interface import IRedisRepository
from config import Config


class RedisRepository(IRedisRepository):
    """
    Handles Redis-specific operations for Pub/Sub related to bids.
    Provides continuous message streaming for SSE connections.
    """

    def __init__(self):
        self.pubsub = None

    def _get_channel(self, job_id: str) -> str:
        return f"{job_id}-{Config.REDIS_BIDS_KEY}"

    async def subscribe(self, job_id: str, redis: RedisClient):
        """
        Subscribe to the Redis Pub/Sub channel for the given job.
        """
        try:
            channel = self._get_channel(job_id)
            self.pubsub = await redis.subscribe(channel)
        except Exception as e:
            raise RuntimeError(f"Failed to subscribe to Redis channel '{channel}': {e}")

    async def unsubscribe(self):
        """
        Unsubscribe and clean up the Redis Pub/Sub connection.
        """
        if not self.pubsub:
            return
        try:
            await self.pubsub.close()
            self.pubsub = None
        except Exception as e:
            raise RuntimeError(f"Failed to close Redis PubSub: {e}")
    
    async def get_existing_bids(self, job_id: str, redis: RedisClient):
        """
        Fetch existing bids stored in Redis (non-pubsub data).
        Returns a JSON string or None.
        """
        try:
            key = f"{job_id}-{Config.REDIS_BIDS_KEY}"
            data = await redis.get(key)
            if not data:
                return "[]"
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            try:
                parsed = json.loads(data)
            except Exception:
                parsed = data
            return json.dumps(parsed)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch existing bids: {e}")    

    async def get_message(self):
        """
        Continuously listens for new messages from the subscribed Redis channel.
        Yields each message as soon as it’s received.
        """
        if not self.pubsub:
            raise RuntimeError("Not subscribed to any Redis channel")

        try:
            async for message in self.pubsub.listen():
                # Skip subscription confirmations and other meta events
                if message.get("type") != "message":
                    continue

                data = message.get("data")
                if isinstance(data, bytes):
                    data = data.decode("utf-8")

                try:
                    payload = json.loads(data)
                except Exception:
                    payload = data  # Send raw string if not JSON

                yield payload

        except asyncio.CancelledError:
            # graceful shutdown on disconnect
            return
        except Exception as e:
            raise RuntimeError(f"Error while listening to Redis Pub/Sub: {e}")
