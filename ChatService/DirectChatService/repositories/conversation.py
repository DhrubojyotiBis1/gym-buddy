from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.conversation import Conversation, ConversationParticipants
from models.enums import ConversationType, Role
from repositories.conversation_interface import IConversationRepository
from logger import get_logger

logger = get_logger()

class ConversationRepository(IConversationRepository):

    async def get_or_create_conversation(self, db: AsyncSession, user1: str, user2: str) -> int:
        logger.info(f"Getting or creating conversation between users: {user1} and {user2}")
        if user1 == user2:
            logger.error("Cannot create a one-to-one conversation with the same user.")
            raise ValueError("Cannot create a one-to-one conversation with the same user.")

        # Sort alphabetically for consistent matching
        users = sorted([user1, user2])

        async with db.begin():
            # 1️⃣ Check if conversation exists
            stmt = (
                select(Conversation.id)
                .join(Conversation.participants)
                .where(
                    Conversation.type == ConversationType.ONE_TO_ONE,
                    ConversationParticipants.user_email.in_(users)
                )
                .group_by(Conversation.id)
                .having(func.count(func.distinct(ConversationParticipants.user_email)) == 2)
            )

            logger.debug(f"Executing select for existing conversation between users {users}")
            result = await db.execute(stmt)
            conversation_id = result.scalars().first()

            if conversation_id:
                logger.info(f"Found existing conversation between {users}: conversation_id={conversation_id}")
                return conversation_id

            # 2️⃣ Create new conversation
            logger.info(f"No existing conversation found between {users}, creating new conversation.")
            new_convo = Conversation(
                type=ConversationType.ONE_TO_ONE,
                created_by=user1,
            )
            db.add(new_convo)
            await db.flush()  # required to get new_convo.id
            logger.debug(f"Created new Conversation: id={new_convo.id}, created_by={user1}")

            # 3️⃣ Insert participants
            participants = [
                ConversationParticipants(
                    user_email=user1,
                    conversation_id=new_convo.id,
                    role=Role.MEMBER,
                ),
                ConversationParticipants(
                    user_email=user2,
                    conversation_id=new_convo.id,
                    role=Role.MEMBER,
                )
            ]

            db.add_all(participants)
            logger.info(f"Added participants [{user1}, {user2}] to conversation id={new_convo.id}")

        logger.info(f"Returning new conversation id={new_convo.id} for users {users}")
        return new_convo.id
