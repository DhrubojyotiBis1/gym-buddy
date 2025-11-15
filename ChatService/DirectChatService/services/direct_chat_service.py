import logging
from connection_services.websocket.websocket_connection_manager_interface import IWebsocketConnectionManager
from repositories.kafka_producer import KafkaProducer
from fastapi import WebSocket
import json

logger = logging.getLogger("direct_chat_service")

class DirectChatService:
    def __init__(self, manager: IWebsocketConnectionManager, kafka_producer: KafkaProducer):
        self.kafka_producer = kafka_producer
        self.manager = manager

    async def send_message(self, data: str, _: str):
        logger.info("Attempting to send message, raw data received: %s", data)
        try:
            json_data = json.loads(data)
            logger.debug(f"Parsed JSON data: {json_data}")
            receiver_id = json_data.get('reciver_id')
            message = json_data.get('message')
            logger.info(f"Preparing to send message to receiver_id: {receiver_id}. Message: {message}")
            # TODO: format data for event
            """
            TODO: Get conversation_id

            Pseudocode:
              - Check if conversation_id is not in Redis:
                  - If not in DB:
                      - Create in DB
                  - Put in Redis
              - Use conversation_id
            """
            # TODO: Write partition finding module 
            partition = ''
            await self.kafka_producer.add_event(data, partition)
            logger.info(f"Message send process for receiver_id: {receiver_id} completed (TODO: actual send logic).")
        except Exception as e:
            logger.error(f"Failed to send message for user {locals().get('receiver_id', None)}: {e}")

    async def add_connection(self, user_id: str, websocket: WebSocket):
        try:
            await self.manager.add_connection(user_id, websocket)
            #TODO: put user_id to microservice discover
            logger.info(f"Added connection for user {user_id}.")
        except Exception as e:
            logger.error(f"Failed to add connection for user {user_id}: {e}")

    async def remove_connection(self, user_id: str):
        try:
            #TODO: put user_id to microservice discover
            await self.manager.remove_connection(user_id)
            logger.info(f"Removed connection for user {user_id}.")
        except Exception as e:
            logger.error(f"Failed to remove connection for user {user_id}: {e}")