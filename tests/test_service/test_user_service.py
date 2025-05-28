"""
User service tests
"""

import pytest
from sqlalchemy.orm import Session

from src.services.user_service import UserService
from src.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_create_user(db_session: Session):
    """Test user creation"""
    user_service = UserService(db_session)
    
    user_data = UserCreate(
        email="test@example.com",
        display_name="Test User"
    )
    
    user = await user_service.create_user("test-id", user_data)
    assert user.email == "test@example.com"
    assert user.display_name == "Test User"


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: Session):
    """Test get user by email"""
    user_service = UserService(db_session)
    
    # First create a user
    user_data = UserCreate(
        email="test2@example.com",
        display_name="Test User 2"
    )
    
    await user_service.create_user("test-id-2", user_data)
    
    # Then try to get it
    found_user = await user_service.get_user_by_email("test2@example.com")
    assert found_user is not None
    assert found_user.email == "test2@example.com"