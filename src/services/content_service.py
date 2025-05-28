"""
Content service layer
"""

import uuid
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Tuple
from fastapi import HTTPException, status

from src.models.content import Content, Category
from src.schemas.content import (
    ContentCreate,
    ContentUpdate,
    CategoryCreate,
    CategoryUpdate,
)


class ContentService:
    """Content service class"""

    def __init__(self, db: Session):
        self.db = db

    # Category methods
    async def create_category(
        self, category_data: CategoryCreate, created_by: str
    ) -> Category:
        """Create a new category"""
        # Check if parent category exists
        if category_data.parent_id:
            parent = await self.get_category_by_id(category_data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent category not found",
                )

        category = Category(category_id=str(uuid.uuid4()), **category_data.model_dump())

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    async def get_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        parent_id: Optional[str] = None,
    ) -> Tuple[List[Category], int]:
        """Get categories with pagination and filters"""
        query = self.db.query(Category)

        # Apply filters
        if is_active is not None:
            query = query.filter(Category.is_active == is_active)

        if parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)

        total = query.count()
        categories = query.offset(skip).limit(limit).all()

        return categories, total

    async def get_category_by_id(self, category_id: str) -> Optional[Category]:
        """Get category by ID"""
        return (
            self.db.query(Category).filter(Category.category_id == category_id).first()
        )

    async def update_category(
        self, category_id: str, category_data: CategoryUpdate
    ) -> Optional[Category]:
        """Update category"""
        category = await self.get_category_by_id(category_id)
        if not category:
            return None

        # Check if parent category exists (if being updated)
        if category_data.parent_id and category_data.parent_id != category.parent_id:
            parent = await self.get_category_by_id(category_data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent category not found",
                )

        # Update fields
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        self.db.commit()
        self.db.refresh(category)
        return category

    async def delete_category(self, category_id: str) -> bool:
        """Delete category (soft delete by setting is_active=False)"""
        category = await self.get_category_by_id(category_id)
        if not category:
            return False

        # Check if category has child categories
        child_categories = (
            self.db.query(Category)
            .filter(Category.parent_id == category_id, Category.is_active.is_(True))
            .count()
        )

        if child_categories > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with active child categories",
            )

        # Check if category has contents
        contents_count = (
            self.db.query(Content)
            .filter(Content.category_id == category_id, Content.is_published.is_(True))
            .count()
        )

        if contents_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with published contents",
            )

        category.is_active = False
        self.db.commit()
        return True

    # Content methods
    async def create_content(
        self, content_data: ContentCreate, created_by: str
    ) -> Content:
        """Create a new content"""
        # Check if category exists
        if content_data.category_id:
            category = await self.get_category_by_id(content_data.category_id)
            if not category or not category.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found or inactive",
                )

        content = Content(
            content_id=str(uuid.uuid4()),
            created_by=created_by,
            **content_data.model_dump(),
        )

        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    async def get_contents(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[str] = None,
        content_type: Optional[str] = None,
        is_published: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Content], int]:
        """Get contents with pagination and filters"""
        query = self.db.query(Content)

        # Apply filters
        if category_id:
            query = query.filter(Content.category_id == category_id)

        if content_type:
            query = query.filter(Content.content_type == content_type)

        if is_published is not None:
            query = query.filter(Content.is_published == is_published)

        if search:
            search_filter = or_(
                Content.title.contains(search), Content.description.contains(search)
            )
            query = query.filter(search_filter)

        # Order by creation date (newest first)
        query = query.order_by(Content.created_at.desc())

        total = query.count()
        contents = query.offset(skip).limit(limit).all()

        return contents, total

    async def get_content_by_id(self, content_id: str) -> Optional[Content]:
        """Get content by ID"""
        return self.db.query(Content).filter(Content.content_id == content_id).first()

    async def update_content(
        self, content_id: str, content_data: ContentUpdate
    ) -> Optional[Content]:
        """Update content"""
        content = await self.get_content_by_id(content_id)
        if not content:
            return None

        # Check if category exists (if being updated)
        if content_data.category_id and content_data.category_id != content.category_id:
            category = await self.get_category_by_id(content_data.category_id)
            if not category or not category.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found or inactive",
                )

        # Update fields
        update_data = content_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(content, field, value)

        self.db.commit()
        self.db.refresh(content)
        return content

    async def delete_content(self, content_id: str) -> bool:
        """Delete content"""
        content = await self.get_content_by_id(content_id)
        if not content:
            return False

        self.db.delete(content)
        self.db.commit()
        return True

    async def publish_content(self, content_id: str) -> Optional[Content]:
        """Publish content"""
        content = await self.get_content_by_id(content_id)
        if not content:
            return None

        content.is_published = True
        self.db.commit()
        self.db.refresh(content)
        return content

    async def unpublish_content(self, content_id: str) -> Optional[Content]:
        """Unpublish content"""
        content = await self.get_content_by_id(content_id)
        if not content:
            return None

        content.is_published = False
        self.db.commit()
        self.db.refresh(content)
        return content
