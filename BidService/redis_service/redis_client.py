from redis_service.redis_connector import RedisConnector
import redis.asyncio as redis
import time
import json
from typing import Optional, Tuple
from config import Config


class RedisClient:
    def __init__(self, connector: RedisConnector):
        self.client = redis.Redis(connection_pool=connector.pool)
    
    #TODO: Use lua stript to do the checking 
    async def add(self, value: str, key: str, stream_key: str) -> bool:
        # value is JSON with fields: amount, user_id, job_id
        try:
            payload = json.loads(value)
            amount = float(payload["amount"])  # raises if missing
            user_id = str(payload.get("user_id", ""))
            job_id = str(payload.get("job_id", ""))
        except Exception:
            return False
        client = self.client
        for _ in range(Config.REDIS_BIDS_RETRY_COUNT):
            #TODO: First check weather or not the job exist 
            pipe = client.pipeline(transaction=True)
            try:
                await pipe.watch(key)
                lowest = await client.zrange(key, 0, 0, withscores=True)
                if lowest:
                    _, lowest_amount = lowest[0]
                    if amount >= lowest_amount:
                        await pipe.reset()
                        return False
                # Composite score: lower amount first, earlier time wins ties
                now = time.time()
                fraction = (now % 1_000_000) / 1_000_000_000_000
                score = amount + fraction
                pipe.multi()
                pipe.xadd(stream_key, {"user_id": user_id, "amount": str(amount), "job_id": job_id})
                #TODO: Fix store dont add fraction find some other way
                pipe.zadd(key, {value: score}, nx=True)
                results = await pipe.execute()
                if not results:
                    return False
                added = bool(results[-1])
                return added
            except redis.WatchError:
                continue
            finally:
                await pipe.reset()
        return False

    async def get_all(self, key: str) -> list[str]:
        members = await self.client.zrange(key, 0, -1)
        return list(members)

    async def get_top(self, key: str) -> str | None:
        members = await self.client.zrevrange(key, 0, 0)
        if not members:
            return None
        return members[0]


connector = RedisConnector()
        
async def get_redis_client() -> RedisClient:
    return RedisClient(connector)

async def close_redis_connection():
    await connector.close()