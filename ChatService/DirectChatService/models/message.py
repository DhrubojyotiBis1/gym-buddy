from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

#TODO: uncomment 
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    body = Column(Text, nullable=True)                       # Message body text
    has_attachment = Column(Boolean, default=False)          # Whether message has an attachment
    visible = Column(Boolean, default=True, nullable=False)  # Soft-delete or hide

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        nullable=False)

    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(),
                        nullable=False)

    # Foreign keys
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    #meta_data_id = Column(Integer, ForeignKey("message_metadata.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    #sender = relationship("User", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")
    #metadata = relationship("MessageMetadata", lazy="joined")
