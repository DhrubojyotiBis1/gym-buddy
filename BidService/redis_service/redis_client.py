from redis_service.redis_connector import RedisConnector
import redis.asyncio as redis
import time
import json
from config import Config


class RedisClient:
    def __init__(self, connector: RedisConnector):
        self.client = redis.Redis(connection_pool=connector.pool)

    async def add(self, value: str, key: str, stream_key: str) -> bool:
        """
        Add a new bid atomically:
        1. Always produce to stream first
        2. Reject bid if stream write fails
        3. Update bid key only if it is lower than the current value
        4. Atomicity ensured using WATCH/MULTI/EXEC
        """
        try:
            payload = json.loads(value)
            amount = float(payload["amount"])
            user_id = str(payload.get("user_id", ""))
            job_id = str(payload.get("job_id", ""))
        except Exception:
            return False

        client = self.client

        for _ in range(Config.REDIS_BIDS_RETRY_COUNT):
            try:
                async with client.pipeline(transaction=True) as pipe:
                    # TODO: Switch to Lua script for atomic compare-and-set with stream append
                    await pipe.watch(key)

                    # First, verify if the job key already exists
                    current_bid = await client.get(key)
                    if current_bid:
                        current_data = json.loads(current_bid)
                        current_amount = float(current_data.get("amount", float("inf")))

                        # Reject if new bid is not better (higher/lower depending on business rule)
                        if amount >= current_amount:
                            await pipe.reset()
                            return False

                    # Add bid entry to stream first (audit + for persistence pipeline)
                    try:
                        await client.xadd(
                            stream_key,
                            {
                                "user_id": user_id,
                                "amount": str(amount),
                                "job_id": job_id,
                                "timestamp": str(time.time()),
                            },
                        )
                    except Exception:
                        # Stream write failed → reject the bid
                        await pipe.reset()
                        return False

                    # Atomic block to update the active bid
                    pipe.multi()
                    pipe.set(key, json.dumps(payload))
                    pipe.publish(key, json.dumps(payload))
                    await pipe.execute()

                    return True  
            except redis.WatchError:
                # Key was modified before EXEC — retry
                continue
            finally:
                await pipe.reset()

        # Failed after retries
        return False
    
    async def get(self, key: str) -> str | None:
        """Retrieve current bid"""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            return value
        except Exception:
            return None


connector = RedisConnector()

async def get_redis_client() -> RedisClient:
    return RedisClient(connector)

async def close_redis_connection():
    await connector.close()