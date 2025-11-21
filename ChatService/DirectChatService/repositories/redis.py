from redis_service.redis_client import RedisClient
from repositories.redis_interface import IRedisInterface
from config import Config
from logger import get_logger

logger = get_logger()

#TODO: Fix execption handling, always raise self.class specific execption exception 
class RedisRepository(IRedisInterface):
    def __init__(
        self,
        connected_user_prefix: str = Config.CONNECTED_USER_PREFIX,
        conversation_users_prefix: str = Config.CONVERSATION_USERS_PREFIX,
        service_identifier: str = Config.SERVICE_IDENTIFIER
    ):
        self.connected_user_prefix = connected_user_prefix
        self.conversation_users_prefix = conversation_users_prefix
        self.service_identifier = service_identifier

    async def put_user_in_connected(self, redis_client: RedisClient, user_id: str) -> None:
        key = f'{self.connected_user_prefix}{user_id}'
        logger.debug(f"Attempting to add user {user_id} with key '{key}' to connected set in Redis.")
        try:
            await redis_client.put_in_set(key, self.service_identifier)
            logger.info(f"User {user_id} successfully added to connected set with key '{key}' in Redis.")
        except Exception as e:
            logger.error(f"Failed to add user {user_id} to connected set: {e}")
            raise e

    async def put_user_in_conversation(self, redis_client: RedisClient, conversation_id: str, user_id: str) -> None:
        key = f"{self.conversation_users_prefix}{conversation_id}"
        logger.debug(f"Attempting to add user {user_id} to conversation {conversation_id} with key '{key}' in Redis.")
        try:
            await redis_client.put_in_set(key, user_id)
            logger.info(f"User {user_id} successfully added to conversation {conversation_id} with key '{key}' in Redis.")
        except Exception as e:
            logger.error(f"Failed to add user {user_id} to conversation {conversation_id}: {e}")
            raise e

    async def removed_user_from_connected(self, redis_client: RedisClient, user_id: str) -> None:
        key = f'{self.connected_user_prefix}{user_id}'
        logger.debug(f"Attempting to remove user {user_id} with key '{key}' from connected set in Redis.")
        try:
            await redis_client.remove(key)
            logger.info(f"User {user_id} successfully removed from connected set with key '{key}' in Redis.")
        except Exception as e:
            logger.error(f"Failed to remove user {user_id} from connected set: {e}")
            raise e
