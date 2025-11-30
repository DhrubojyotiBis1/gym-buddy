from logger import get_logger
from services.websocket.websocket_connection_manager_interface import IWebsocketConnectionManager
from repositories.redis_interface import IRedisInterface
from repositories.kafka_producer import KafkaProducer
from fastapi import WebSocket, WebSocketDisconnect, status
from repositories.conversation_interface import IConversationRepository
from sqlalchemy.ext.asyncio import AsyncSession
from redis_service.redis_client import RedisClient
from services.kafka.kafka_client import KafkaClient 
import json

logger = get_logger()

class DirectChatService:
    def __init__(
        self, 
        manager: IWebsocketConnectionManager, 
        kafka_producer: KafkaProducer, 
        redis: IRedisInterface,
        conversation: IConversationRepository
    ):
        self.manager = manager
        self.kafka_producer = kafka_producer
        self.redis = redis
        self.conversation = conversation

    async def send_message(
        self, 
        db: AsyncSession, 
        kafka_client: KafkaClient, 
        redis_client: RedisClient, 
        data: str, 
        sender_email: str
    ):
        logger.info("Attempting to send message, raw data received: %s", data)
        reciver_email = None
        conversation_id = None
        try:
            json_data = json.loads(data)
            logger.debug(f"Parsed JSON data: {json_data}")

            conversation_id = json_data.get('conversation_id')
            message = json_data.get('message')
            reciver_email = json_data.get('reciver_email')

            logger.info("Preparing to send message to conversation_id: %s. Message: %s", conversation_id, message)

            # If conversation_id not supplied, obtain or create conversation
            if not conversation_id:
                if not reciver_email:
                    error_msg = "Receiver email must be provided when conversation_id is not present."
                    logger.error(error_msg)
                    raise ValueError(error_msg)

                logger.info("Conversation id not found, getting/creating new conversation. Sender: %s, Receiver: %s", sender_email, reciver_email)
                conversation_id = await self.redis.get_conversation_id(redis_client, sender_email, reciver_email)
                logger.debug("Result of redis.get_conversation_id: %s", conversation_id)
                
                if not conversation_id:
                    logger.info("No conversation id in redis for (%s, %s), creating new in DB.", sender_email, reciver_email)
                    conversation_id = await self.conversation.get_or_create_conversation(db, reciver_email, sender_email)
                    logger.info("Created new conversation id: %s", conversation_id)

                # Store conversation id for both users in Redis
                logger.info("Storing conversation id %s in redis for users (%s, %s)", conversation_id, sender_email, reciver_email)
                await self.redis.put_conversation_id_for_users(redis_client, sender_email, reciver_email, conversation_id)

                logger.debug("Adding sender (%s) and receiver (%s) to conversation id %s in redis.", sender_email, reciver_email, conversation_id)
                await self.redis.put_user_in_conversation(redis_client, conversation_id, sender_email)
                await self.redis.put_user_in_conversation(redis_client, conversation_id, reciver_email)

                # Notify sender of conversation info
                info_msg = f'type: INFO, details: conversation_id {conversation_id}'
                logger.info("Sending info message to sender %s: %s", sender_email, info_msg)
                await self.manager.send_message_to_user(info_msg, sender_email)
                logger.debug("Sent conversation info to sender.")

            # Format payload for Kafka and send message
            kafka_producer_data = {
                'text': json_data.get('text'), 
                'sender_email': sender_email, 
                'conversation_id': conversation_id
            }
            logger.info("Adding event to Kafka, conversation_id: %s", conversation_id)
            await self.kafka_producer.add_event(
                kafka_client, 
                json.dumps(kafka_producer_data), 
                str(conversation_id)
            )
            logger.info(f"Message send process for conversation_id: {conversation_id} completed.")
        except Exception as e:
            logger.error(f"Failed to send message for user {reciver_email if reciver_email else sender_email}: {e}", exc_info=True)
            raise

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
            # Not removing from redis increases delivery service overhead
            # await self.redis.removed_user_from_connected(redis_client, user_id)
            await self.manager.disconnect(user_id)
            logger.info(f"Removed connection for user {user_id}.")
        except Exception as e:
            error_msg = f"Failed to remove connection for user {user_id}: {e}"
            logger.error(error_msg)
            raise WebSocketDisconnect(code=status.WS_1011_INTERNAL_ERROR, reason=error_msg)