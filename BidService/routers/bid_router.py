from fastapi import APIRouter, Depends, status, Query
from typing import List
from schemas.bid import BidResponse, BidRequest
from services.bid_service import BidService
from repositories.redis_repository import RedisRepository
from jwt_service.jwt_service import verify_jwt
from redis_service.redis_client import RedisClient, get_redis_client

router = APIRouter(prefix="/bid", tags=["Bids"])
bid_service = BidService(RedisRepository())


@router.get("/", response_model=List[BidResponse])
async def list_bids(
    _=Depends(verify_jwt),
    job_id: str = Query(..., description="Filter by job ID (required string)"),
    redis: RedisClient = Depends(get_redis_client),
):
    return await bid_service.list_bids(job_id, redis)

@router.post("/", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
async def create_bid(bid: BidRequest, user=Depends(verify_jwt), redis: RedisClient = Depends(get_redis_client)):
    return await bid_service.create_bid(user, bid, redis)