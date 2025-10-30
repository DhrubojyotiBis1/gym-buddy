from repositories.redis_interface import IRedisRepository
from redis_service.redis_client import RedisClient
from schemas.bid import BidCreate, BidRequest, BidResponse
from typing import List
import json
from starlette.exceptions import HTTPException as StarletteHTTPException


class BidService:
	def __init__(self, redis_repo: IRedisRepository):
		self.redis_repo = redis_repo
	
	async def list_bids(self, job_id: str, redis_client: RedisClient) -> List[BidResponse]:
		try:
			members = await self.redis_repo.get_all_bids(job_id, redis_client)
			# members are JSON strings stored in the sorted set; map to BidResponse
			responses: List[BidResponse] = []
			for m in members:
				obj = json.loads(m)
				responses.append(BidResponse(
					id='',
					amount=obj.get('amount'),
					user_id=obj.get('user_id'),
					job_id=obj.get('job_id'),
				))
			return responses
		except StarletteHTTPException:
			raise
		except Exception:
			raise StarletteHTTPException(status_code=500, detail='Failed to list bids')
	
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
