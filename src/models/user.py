"""
User model
"""

from sqlalchemy import Column, String, Boolean
from src.models.base import BaseModel


class User(BaseModel):
    """User model"""
    
    __tablename__ = "users"
    
    user_id = Column(String(36), primary_key=True, index=True)
    google_user_id = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    department = Column(String(100))
    position = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)