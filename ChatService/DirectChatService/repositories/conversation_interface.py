from abc import ABC, abstractmethod

class IConversationRepository(ABC):
    @abstractmethod
    async def get_or_create_conversation(self, user1: str, user2: str) -> str:
        """
        Retrieves the conversation ID for the two users if it exists,
        otherwise creates a new conversation and returns its ID.
        """
        pass
