from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from models.enums import ConversationType, Role
from models.user import User


#TODO: Remove all comments
class ConversationParticipants(Base):
    __tablename__ = "conversation_participants"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_email = Column(String, ForeignKey("users.email", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    #last_read_message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)

    role = Column(Enum(Role), nullable=False)
    joining_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    #user = relationship("User", back_populates="conversation_participants", lazy="joined")
    conversation = relationship("Conversation", back_populates="participants", lazy="joined")
    #last_read = relationship("Message", lazy="joined")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    # FK to users.id – conversation creator
    created_by = Column(String, ForeignKey("users.email", ondelete="SET NULL"), nullable=True)

    # Metadata fields
    title = Column(String, nullable=True)
    type = Column(Enum(ConversationType), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(),
                        nullable=False)

    # Relationships
    """
    creator = relationship("User",
                           back_populates="created_conversations",
                           foreign_keys=[created_by],
                           lazy="joined")
    """

    participants = relationship("ConversationParticipants",
                                back_populates="conversation",
                                cascade="all, delete-orphan",
                                lazy="joined")
