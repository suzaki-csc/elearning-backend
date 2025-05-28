"""
Content API endpoints
"""

import math
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from src.config.database import get_db
from src.api.v1.deps import get_current_user, get_current_active_admin
from src.models.user import User
from src.services.content_service import ContentService
from src.schemas.content import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    ContentListResponse,
    ContentType,
)

router = APIRouter()


# Category endpoints
@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Create a new category (Admin only)"""
    content_service = ContentService(db)
    return await content_service.create_category(category_data, current_user.user_id)


@router.get("/categories", response_model=CategoryListResponse)
async def get_categories(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    parent_id: Optional[str] = Query(None, description="Filter by parent category"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get categories with pagination and filters"""
    content_service = ContentService(db)
    skip = (page - 1) * per_page

    categories, total = await content_service.get_categories(
        skip=skip, limit=per_page, is_active=is_active, parent_id=parent_id
    )

    total_pages = math.ceil(total / per_page)

    return CategoryListResponse(
        categories=categories,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get category by ID"""
    content_service = ContentService(db)
    category = await content_service.get_category_by_id(category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Update category (Admin only)"""
    content_service = ContentService(db)
    category = await content_service.update_category(category_id, category_data)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return category


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Delete category (Admin only)"""
    content_service = ContentService(db)
    success = await content_service.delete_category(category_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return {"message": "Category deleted successfully"}


# Content endpoints
@router.post("/", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Create a new content (Admin only)"""
    content_service = ContentService(db)
    return await content_service.create_content(content_data, current_user.user_id)


@router.get("/", response_model=ContentListResponse)
async def get_contents(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    content_type: Optional[ContentType] = Query(
        None, description="Filter by content type"
    ),
    is_published: Optional[bool] = Query(
        None, description="Filter by published status"
    ),
    search: Optional[str] = Query(None, description="Search in title and description"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get contents with pagination and filters"""
    content_service = ContentService(db)
    skip = (page - 1) * per_page

    contents, total = await content_service.get_contents(
        skip=skip,
        limit=per_page,
        category_id=category_id,
        content_type=content_type.value if content_type else None,
        is_published=is_published,
        search=search,
    )

    total_pages = math.ceil(total / per_page)

    return ContentListResponse(
        contents=contents,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get content by ID"""
    content_service = ContentService(db)
    content = await content_service.get_content_by_id(content_id)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    # Check if user can access unpublished content
    if not content.is_published and content.created_by != current_user.user_id:
        # TODO: Add admin role check here
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to unpublished content",
        )

    return content


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: str,
    content_data: ContentUpdate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Update content (Admin only)"""
    content_service = ContentService(db)
    content = await content_service.update_content(content_id, content_data)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    return content


@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Delete content (Admin only)"""
    content_service = ContentService(db)
    success = await content_service.delete_content(content_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    return {"message": "Content deleted successfully"}


@router.post("/{content_id}/publish", response_model=ContentResponse)
async def publish_content(
    content_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Publish content (Admin only)"""
    content_service = ContentService(db)
    content = await content_service.publish_content(content_id)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    return content


@router.post("/{content_id}/unpublish", response_model=ContentResponse)
async def unpublish_content(
    content_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Unpublish content (Admin only)"""
    content_service = ContentService(db)
    content = await content_service.unpublish_content(content_id)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    return content
