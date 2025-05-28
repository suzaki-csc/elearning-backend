"""
Content model
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from src.models.base import BaseModel


class Category(BaseModel):
    """Category model"""

    __tablename__ = "categories"

    category_id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(String(36), ForeignKey("categories.category_id"))
    is_active = Column(Boolean, default=True, nullable=False)


class Content(BaseModel):
    """Content model"""

    __tablename__ = "contents"

    content_id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category_id = Column(String(36), ForeignKey("categories.category_id"))
    content_type = Column(String(50), nullable=False)
    file_path = Column(String(500))
    duration_minutes = Column(Integer)
    is_published = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(36), ForeignKey("users.user_id"))
