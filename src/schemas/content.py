"""
Content schemas (placeholder)
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContentBase(BaseModel):
    """Base content schema"""
    title: str
    description: Optional[str] = None
    content_type: str


class ContentCreate(ContentBase):
    """Content creation schema"""
    category_id: Optional[str] = None


class ContentResponse(ContentBase):
    """Content response schema"""
    content_id: str
    category_id: Optional[str]
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True