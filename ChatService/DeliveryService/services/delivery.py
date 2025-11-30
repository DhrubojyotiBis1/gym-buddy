from repositories.redis_repository_interface import IRedisRepository
from services.kafka.kafka_client import KafkaClient
from services.redis.redis_connector_interface import IRedisConnector
from services.direct_chat_gprc.connection_manager_interface import IConnectionManager
from services.kafka.kafka_connector_interface import IKafkaConnector
from services.direct_chat_gprc.direct_chat_client import DirectChatClient
from services.kafka.kafka_client import KafkaClient
from config import Config
from logger import get_logger
import json

logger = get_logger()

class DeliveryService:
    def __init__(self, kafka_connector: IKafkaConnector, redis: IRedisRepository, connection_manager: IConnectionManager):
        self.kafka_connector = kafka_connector
        self.redis = redis
        self.connection_manager = connection_manager
    
    async def start(self, redis_connector: IRedisConnector):
        logger.info("DeliveryService started consuming messages.")
        async for msg in KafkaClient.consume(
            topics=[Config.KAFKA_CONSUMER_TOPIC], 
            group_id=Config.KAFKA_CONSUMER_GROUP_ID,
            connector=self.kafka_connector):

            logger.info(f"Received message from Kafka: {msg!r}")

            # Parse actual message, conversation_id, sender from 'msg'
            msg_data = json.loads(msg.value.decode() if hasattr(msg.value, 'decode') else msg.value)
            conversation_id = msg_data.get("conversation_id")
            message = msg_data.get("text")
            sender_email = msg_data.get("sender_email")

            logger.debug(f"Extracted conversation_id='{conversation_id}', message='{message}', sender_email='{sender_email}' from Kafka message")

            try:
                participants = await self.redis.get_participants(redis_connector, conversation_id)
                if participants is None:
                    logger.warning(f"No participants found for conversation_id: {conversation_id}. Skipping message delivery.")
                    continue
                logger.info(f"Fetched participants for conversation_id '{conversation_id}': {participants}")
                
                # TODO: Do this in parallel for better performance
                for receiver_email in participants:
                    logger.debug(f"Processing receiver_email='{receiver_email}' (message sender: '{sender_email}') for message forwarding.")
                    if sender_email == receiver_email:
                        logger.info(f"Skipping sender '{sender_email}' from message delivery loop.")
                        continue
                    service = await self.redis.get_service_for(redis_connector, receiver_email)
                    if not service:
                        logger.warning(f"No service info found for receiver '{receiver_email}'. Skipping delivery.")
                        continue
                    logger.info(f"Fetched service info for receiver '{receiver_email}': {service}")
                    try:
                        logger.debug(
                            f"Sending message to DirectChatClient: receiver_email='{receiver_email}', host='{service.get('host')}', port='{service.get('port')}', sender_email='{sender_email}'"
                        )
                        await DirectChatClient.send_message(
                            self.connection_manager,
                            message,
                            service.get('host'), 
                            service.get('port'), 
                            receiver_email, 
                            sender_email
                        )
                        logger.info(f"Message sent to direct chat service successfully for receiver '{receiver_email}'.")
                    except Exception as chat_exc:
                        logger.error(f"Failed to send message to receiver '{receiver_email}' via direct chat service: {chat_exc}", exc_info=True)
            except Exception as e:
                logger.error(f"Error processing Kafka message for conversation_id '{conversation_id}': {e}", exc_info=True)