"""
User service layer
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate


class UserService:
    """User service class"""

    def __init__(self, db: Session):
        self.db = db

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.user_id == user_id).first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    async def create_user(self, user_id: str, user_data: UserCreate) -> User:
        """Create new user"""
        db_user = User(user_id=user_id, **user_data.model_dump())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        db_user = await self.get_user_by_id(user_id)
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete)"""
        db_user = await self.get_user_by_id(user_id)
        if not db_user:
            return False

        db_user.is_active = False
        self.db.commit()
        return True
