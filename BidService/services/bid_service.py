from repositories.redis_interface import IRedisRepository
from redis_service.redis_client import RedisClient
from schemas.bid import BidCreate, BidRequest, BidResponse
from typing import List
import json
from starlette.exceptions import HTTPException as StarletteHTTPException


class BidService:
	def __init__(self, redis_repo: IRedisRepository):
		self.redis_repo = redis_repo
	
	async def get_bid(self, job_id: str, redis_client: RedisClient) -> BidResponse:
		try:
			member = await self.redis_repo.get(job_id, redis_client)
			if not member:
				raise StarletteHTTPException(status_code=404, detail="Bid not found")
			# member should be a dict at this point
			return BidResponse(
				id='',
				amount=member.get('amount'),
				user_id=member.get('user_id'),
				job_id=member.get('job_id'),
			)
		except StarletteHTTPException:
			raise
		except Exception:
			raise StarletteHTTPException(status_code=500, detail='Failed to get bid')
	
	async def create_bid(self, user: str, bid_request: BidRequest, redis_client: RedisClient) -> BidResponse:
		try:
			bid = BidCreate(user_id=user, amount=bid_request.amount, job_id=bid_request.job_id)
			added = await self.redis_repo.add_bid(bid, redis_client)
			if not added:
				raise StarletteHTTPException(status_code=400, detail='Bid already exists')
			resp = BidResponse(
				id='',
				amount=bid.amount,
				user_id=bid.user_id,
				job_id=bid.job_id,
			)
			return resp
		except StarletteHTTPException:
			raise
		except Exception:
			raise StarletteHTTPException(status_code=500, detail='Failed to create bid')
