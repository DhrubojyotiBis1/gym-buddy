from logger import get_logger
from services.websocket.websocket_connection_manager_interface import IWebsocketConnectionManager
from repositories.redis import RedisRepository
from repositories.kafka_producer import KafkaProducer
from fastapi import WebSocket, WebSocketDisconnect, status
from repositories.conversation import ConversationRepository
import json
from sqlalchemy.ext.asyncio import AsyncSession
from redis_service.redis_client import RedisClient
from services.kafka.kafka_client import KafkaClient 

logger = get_logger()

#TODO: Fix execption handling, always raise self.class specific execption exception 
class DirectChatService:
    def __init__(self, manager: IWebsocketConnectionManager, kafka_producer: KafkaProducer, redis: RedisRepository,
     conversation: ConversationRepository):
        self.kafka_producer = kafka_producer
        self.manager = manager
        self.redis = redis
        self.conversation = conversation

    async def send_message(self, db: AsyncSession, kafka_client: KafkaClient, data: str, sender_email: str):
        logger.info("Attempting to send message, raw data received: %s", data)
        try:
            json_data = json.loads(data)
            logger.debug(f"Parsed JSON data: {json_data}")
            conversation_id = json_data.get('conversation_id')
            message = json_data.get('message')
            logger.info(f"Preparing to send message to conversation_id: {conversation_id}. Message: {message}")
            # TODO: format data for event

            if not conversation_id:
                reciver_email = json_data.get('reciver_email')
                logger.info(f"Conersation id not found geting/creating new conversation")
                conversation_id = await self.conversation.get_or_create_conversation(db, reciver_email, sender_email)
                #TODO: Send conversation id for first time conversation (1:1 case)
            
            await self.kafka_producer.add_event(kafka_client, data, str(conversation_id))
            logger.info(f"Message send process for conversation_id: {conversation_id} completed (TODO: actual send logic).")
        except Exception as e:
            logger.error(f"Failed to send message for user {reciver_email}: {e}")

    async def add_connection(self, redis_client: RedisClient, user_id: str, websocket: WebSocket):
        try:
            await self.manager.connect(user_id, websocket)
            await self.redis.put_user_in_connected(redis_client, user_id)
            logger.info(f"Added connection for user {user_id}.")
        except Exception as e:
            error_msg = f"Failed to add connection for user {user_id}: {e}"
            logger.error(error_msg)
            raise WebSocketDisconnect(code=status.WS_1011_INTERNAL_ERROR, reason=error_msg)

    async def remove_connection(self, _: RedisClient, user_id: str):
        try:
            #Not removing from redis increases delivery service overhead
            #await self.redis.removed_user_from_connected(redis_client, user_id)
            await self.manager.disconnect(user_id)
            logger.info(f"Removed connection for user {user_id}.")
        except Exception as e:
            error_msg = f"Failed to remove connection for user {user_id}: {e}"
            logger.error(error_msg)
            raise WebSocketDisconnect(code=status.WS_1011_INTERNAL_ERROR, reason=error_msg)