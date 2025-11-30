from repositories.redis_repository_interface import IRedisRepository
from services.redis.redis_connector_interface import IRedisConnector
from services.redis.redis_client import RedisClient
from config import Config
from logger import get_logger

logger = get_logger()

class RedisRepository(IRedisRepository):
    async def get_participants(self, redis_connector: IRedisConnector, conversation_id: str):
        """
        Fetches the participants of a conversation from Redis.

        Args:
            redis_connector (IRedisConnector): The Redis connector interface.
            conversation_id (str): The ID of the conversation.

        Returns:
           list
        """
        key = f"{Config.CONVERSATION_ID_USERS_PREFIX}{conversation_id}"
        logger.debug(f"Fetching participants for conversation_id: {conversation_id} using key: {key}")
        result = await RedisClient.get_from_set(redis_connector, key)
        if result is None:
            logger.info(f"No participants found in Redis for conversation_id: {conversation_id}")
            return None

        logger.info(f"Fetched participants from Redis for conversation_id: {conversation_id}")
        return result

    async def get_service_for(self, redis_connector: IRedisConnector, receiver_email: str):
        """
        Fetches the service associated with a receiver from Redis.

        Args:
            redis_connector (IRedisConnector): The Redis connector interface.
            receiver_email (str): The receiver's email.

        Returns:
            str or None: The service name or None if not found.
        """
        key = f'{Config.USERS_SERVICE_PREFIX}{receiver_email}'
        logger.debug(f"Fetching service for receiver_email: {receiver_email} using key: {key}")
        result = await RedisClient.get_from_hash(redis_connector, key)
        # According to RedisClient implementation, decoding shouldn't be necessary,
        # but if bytes are returned, decode for compatibility.
        if result is not None and isinstance(result, bytes):
            decoded = result.decode()
            logger.info(f"Service for receiver_email {receiver_email} found in Redis: {decoded}")
            return decoded
        logger.info(f"Service for receiver_email {receiver_email} in Redis: {result}")
        return result

