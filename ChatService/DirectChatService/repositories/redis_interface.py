from abc import ABC, abstractmethod

class IRedisInterface(ABC):
    @abstractmethod
    async def put_user_in_connected(self, user_id: str) -> None:
        """
        Adds a user to the connected set in Redis.
        """
        pass

    @abstractmethod
    async def put_user_in_conversation(self, conversation_id: str, user_id: str) -> None:
        """
        Adds a user to a given conversation in Redis.
        """
        pass

    @abstractmethod
    async def removed_user_from_connected(self, user_id: str) -> None:
        """
        Removes a user from the connected set in Redis.
        """
        pass
