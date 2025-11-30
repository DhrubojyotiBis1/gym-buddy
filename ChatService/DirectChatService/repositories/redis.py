from redis_service.redis_client import RedisClient
from repositories.redis_interface import IRedisInterface
from config import Config
from logger import get_logger
from typing import Optional, Any


logger = get_logger()

class RedisRepository(IRedisInterface):
    class RedisRepositoryException(Exception):
        pass

    def __init__(
        self,
        connected_user_prefix: str = Config.CONNECTED_USER_PREFIX,
        user_conversation_id_prefix: str = Config.USERS_CONVERSATION_ID_PREFIX,
        service_host: str = Config.SERVICE_HOST, 
        service_port: str = Config.SERVICE_PORT, 
        conversation_id_user_prefix: str = Config.CONVERSATION_ID_USER_PREFIX
    ):
        self.connected_user_prefix = connected_user_prefix
        self.user_conversation_id_prefix = user_conversation_id_prefix
        self.conversation_id_user_prefix = conversation_id_user_prefix
        self.service_identifier = {"host": service_host, "port": service_port}

    async def put_user_in_connected(self, redis_client: RedisClient, user_id: str) -> None:
        key = f"{self.connected_user_prefix}{user_id}"
        logger.debug(f"[RedisRepository] Adding user '{user_id}' with key '{key}' to connected set in Redis.")
        try:
            await redis_client.put_in_hash(key, self.service_identifier)
            logger.info(f"[RedisRepository] User '{user_id}' added to connected set with key '{key}'.")
        except Exception as e:
            logger.error(f"[RedisRepository] Failed to add user '{user_id}' to connected set: {e}")
            raise self.RedisRepositoryException(
                f"Failed to add user '{user_id}' to connected set"
            ) from e

    async def get_conversation_id(
        self, redis_client: RedisClient, user1: str, user2: str
    ) -> Optional[str]:
        users_sorted = sorted([user1, user2])
        key = f"{self.user_conversation_id_prefix}{users_sorted[0]}_{users_sorted[1]}"
        logger.debug(f"[RedisRepository] Fetching conversation_id for users '{user1}', '{user2}' with key '{key}'.")
        try:
            conversation_id = await redis_client.get(key)
            if conversation_id:
                logger.info(f"[RedisRepository] Found conversation_id '{conversation_id}' for users '{user1}', '{user2}'.")
            else:
                logger.info(f"[RedisRepository] No conversation_id found for users '{user1}', '{user2}'.")
            return conversation_id
        except Exception as e:
            logger.error(f"[RedisRepository] Error fetching conversation_id for users '{user1}', '{user2}': {e}")
            raise self.RedisRepositoryException(
                f"Error fetching conversation_id for users '{user1}', '{user2}'"
            ) from e

    async def put_conversation_id_for_users(
        self, redis_client: RedisClient, user1: str, user2: str, conversation_id: str
    ) -> None:
        users_sorted = sorted([user1, user2])
        key = f"{self.user_conversation_id_prefix}{users_sorted[0]}_{users_sorted[1]}"
        logger.debug(f"[RedisRepository] Storing conversation_id '{conversation_id}' for users '{user1}', '{user2}' with key '{key}'.")
        try:
            await redis_client.put(key, conversation_id)
            logger.info(f"[RedisRepository] Stored conversation_id '{conversation_id}' for users '{user1}', '{user2}' with key '{key}'.")
        except Exception as e:
            logger.error(f"[RedisRepository] Failed to store conversation_id '{conversation_id}' for users '{user1}', '{user2}': {e}")
            raise self.RedisRepositoryException(
                f"Failed to store conversation_id '{conversation_id}' for users '{user1}', '{user2}'"
            ) from e

    async def put_user_in_conversation(
        self, redis_client: RedisClient, conversation_id: str, user_id: str
    ) -> None:
        key = f"{self.conversation_id_user_prefix}{conversation_id}"
        logger.debug(f"[RedisRepository] Adding user '{user_id}' to conversation '{conversation_id}' with key '{key}'.")
        try:
            await redis_client.put_in_set(key, user_id)
            logger.info(f"[RedisRepository] User '{user_id}' added to conversation '{conversation_id}' with key '{key}'.")
        except Exception as e:
            logger.error(f"[RedisRepository] Failed to add user '{user_id}' to conversation '{conversation_id}': {e}")
            raise self.RedisRepositoryException(
                f"Failed to add user '{user_id}' to conversation '{conversation_id}'"
            ) from e

    async def removed_user_from_connected(self, redis_client: RedisClient, user_id: str) -> None:
        key = f"{self.connected_user_prefix}{user_id}"
        logger.debug(f"[RedisRepository] Removing user '{user_id}' with key '{key}' from connected set in Redis.")
        try:
            await redis_client.remove(key)
            logger.info(f"[RedisRepository] User '{user_id}' removed from connected set with key '{key}'.")
        except Exception as e:
            logger.error(f"[RedisRepository] Failed to remove user '{user_id}' from connected set: {e}")
            raise self.RedisRepositoryException(
                f"Failed to remove user '{user_id}' from connected set"
            ) from e

