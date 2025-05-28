"""
Content schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    """Content type enumeration"""

    VIDEO = "video"
    DOCUMENT = "document"
    QUIZ = "quiz"
    PRESENTATION = "presentation"
    INTERACTIVE = "interactive"


# Category schemas
class CategoryBase(BaseModel):
    """Base category schema"""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Category creation schema"""

    pass


class CategoryUpdate(BaseModel):
    """Category update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Category response schema"""

    category_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Content schemas
class ContentBase(BaseModel):
    """Base content schema"""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content_type: ContentType
    category_id: Optional[str] = None
    file_path: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)


class ContentCreate(ContentBase):
    """Content creation schema"""

    pass


class ContentUpdate(BaseModel):
    """Content update schema"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    category_id: Optional[str] = None
    file_path: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    is_published: Optional[bool] = None


class ContentResponse(ContentBase):
    """Content response schema"""

    content_id: str
    is_published: bool
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentListResponse(BaseModel):
    """Content list response schema"""

    contents: List[ContentResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class CategoryListResponse(BaseModel):
    """Category list response schema"""

    categories: List[CategoryResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
