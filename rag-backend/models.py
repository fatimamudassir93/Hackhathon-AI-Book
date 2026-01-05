"""
SQLAlchemy models for Physical AI Book application
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    personalizations = relationship("PersonalizationCache", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    technical_level = Column(String(50), nullable=False)  # beginner, intermediate, advanced
    programming_experience = Column(ARRAY(String))  # ['python', 'javascript', 'ros']
    robotics_background = Column(String(50))  # none, hobbyist, professional, researcher
    learning_goals = Column(Text)
    preferred_language = Column(String(10), default='en')  # en, ur
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="profile")


class PersonalizationCache(Base):
    __tablename__ = "personalization_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    chapter_id = Column(String(100), nullable=False)
    personalized_content = Column(Text, nullable=False)
    language = Column(String(10), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="personalizations")

    __table_args__ = (
        # Unique constraint on user_id, chapter_id, and language
        # This ensures one cached personalization per user per chapter per language
    )


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    sources = Column(JSON)  # Store source citations as JSON
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="chat_history")
