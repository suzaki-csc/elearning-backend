"""
User model
"""

from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class User(BaseModel):
    """User model"""

    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, index=True)
    google_user_id = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(
        String(255), nullable=True
    )  # Nullable for Google OAuth users
    display_name = Column(String(100), nullable=False)
    department = Column(String(100))
    position = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)
    refresh_token = Column(Text, nullable=True)  # Store refresh token

    # Relationships
    learning_progress = relationship("LearningProgress", back_populates="user")
