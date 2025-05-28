"""
User API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from src.config.database import get_db
from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.services.user_service import UserService
from src.models.user import User

router = APIRouter()


# Temporary function for development - replace with proper auth later
async def get_current_user_temp() -> User:
    """Temporary current user for development"""
    # TODO: Replace with proper JWT authentication
    temp_user = User(
        user_id=str(uuid.uuid4()),
        email="admin@example.com",
        display_name="Admin User",
        is_active=True
    )
    return temp_user


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all users"""
    user_service = UserService(db)
    users = await user_service.get_users(skip=skip, limit=limit)
    return users


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user_temp)
):
    """Get current user information"""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create new user"""
    user_service = UserService(db)
    
    # Check if user already exists
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Generate UUID for new user
    user_id = str(uuid.uuid4())
    user = await user_service.create_user(user_id=user_id, user_data=user_data)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user"""
    user_service = UserService(db)
    user = await user_service.update_user(user_id=user_id, user_data=user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user