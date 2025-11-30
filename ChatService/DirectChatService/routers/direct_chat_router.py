from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from jwt_service.jwt_service import verify_jwt
from services.direct_chat_service import DirectChatService
from services.websocket.manager import WebsocketConnectionManager
from repositories.kafka_producer import KafkaProducer
from repositories.redis import RedisRepository
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.kafka.kafka_client import get_kafka_client
from redis_service.redis_client import get_redis_client
from repositories.conversation import ConversationRepository
from fastapi.responses import Response


router = APIRouter(
    prefix="/direct-chat",
    tags=["Direct Chat"]
)

direct_chat_service = DirectChatService(WebsocketConnectionManager(), KafkaProducer(), RedisRepository(), ConversationRepository())

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
    kafka_client=Depends(get_kafka_client),
    user=Depends(verify_jwt),
    redis = Depends(get_redis_client)
):
    await direct_chat_service.add_connection(redis, user, websocket)
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await direct_chat_service.send_message(db, kafka_client, redis, data, user)
    except WebSocketDisconnect:
        await direct_chat_service.remove_connection(redis, user)
        return Response(status_code=200)
