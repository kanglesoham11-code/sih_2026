"""
User, Conversation, and Message models
"""

import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model - PRD Section 27.2"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20), unique=True, index=True)
    display_name = Column(String(255))
    role = Column(String(50), nullable=False, default="user")  # user|researcher|admin
    language_pref = Column(String(10), nullable=False, default="en")
    last_login_at = Column(DateTime)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class Conversation(Base, TimestampMixin):
    """Conversation model"""
    
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    title = Column(String(500))
    language = Column(String(10))
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation {self.id}>"


class Message(Base):
    """Message model"""
    
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user|assistant|system|tool
    content = Column(Text, nullable=False)
    query_mode = Column(String(20))  # standard|live
    answer_id = Column(UUID(as_uuid=True))  # Links to recommendations
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.role} at {self.created_at}>"
