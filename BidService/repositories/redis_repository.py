from repositories.redis_interface import IRedisRepository
from redis_service.redis_client import RedisClient
from schemas.bid import BidCreate
from config import Config
from typing import Optional, Tuple


class RedisRepository(IRedisRepository):

	async def add_bid(self, bid: BidCreate, redis: RedisClient) -> bool:
		key = f"{bid.job_id}-{Config.REDIS_BIDS_KEY}"
		stream_key = f"{bid.job_id}-{Config.REDIS_STREAM_KEY}"
		added = await redis.add(bid.model_dump_json(by_alias=True), key, stream_key)
		return added

	async def get_all_bids(self, job_id: str, redis: RedisClient):
		key = f"{job_id}-{Config.REDIS_BIDS_KEY}"
		return await redis.get_all(key)
