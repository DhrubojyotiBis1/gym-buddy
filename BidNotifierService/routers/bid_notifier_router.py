from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from jwt_service.jwt_service import verify_jwt
from services.bid_notifier_service import BidNotifierService
from redis_service.redis_client import RedisClient, get_redis_client
from repositories.redis_repository import RedisRepository


router = APIRouter(prefix="/bid-notifier", tags=["Bid Notifier"])
bid_notifier_service = BidNotifierService(RedisRepository())


@router.get("/connect")
async def connect_to_bid_stream(
    job_id: str = Query(..., description="The Job ID to listen for bid updates"),
    redis: RedisClient = Depends(get_redis_client),
):
    """
    Establishes an SSE connection for real-time bid updates for a specific job.
    The client stays connected and receives updates as new bids come in.
    """
    event_stream = bid_notifier_service.listen_to_bid(job_id, redis)
    return StreamingResponse(event_stream, media_type="text/event-stream")
