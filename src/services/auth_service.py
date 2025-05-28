"""
Authentication service layer
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.config.settings import settings
from src.models.user import User
from src.schemas.auth import TokenData, UserRegistration
from src.services.user_service import UserService

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service class"""

    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token"""
        data = {
            "sub": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=30),  # 30 days
        }
        return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                return None

            token_data = TokenData(user_id=user_id)
            return token_data
        except JWTError:
            return None

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.user_service.get_user_by_email(email)
        if not user:
            return None

        if not user.password_hash:
            return None  # User registered via OAuth, no password set

        if not self.verify_password(password, user.password_hash):
            return None

        return user

    async def register_user(self, user_data: UserRegistration) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self.user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        # Hash password
        password_hash = self.get_password_hash(user_data.password)

        # Create user
        user_id = str(uuid.uuid4())
        user = User(
            user_id=user_id,
            email=user_data.email,
            password_hash=password_hash,
            display_name=user_data.display_name,
            department=user_data.department,
            position=user_data.position,
            is_active=True,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def login_user(self, email: str, password: str) -> dict:
        """Login user and return tokens"""
        user = await self.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.user_id, "email": user.email},
            expires_delta=access_token_expires,
        )

        refresh_token = self.create_refresh_token(user.user_id)

        # Store refresh token in database
        user.refresh_token = refresh_token
        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")

            if user_id is None or token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Verify refresh token exists in database
        user = await self.user_service.get_user_by_id(user_id)
        if not user or user.refresh_token != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.user_id, "email": user.email},
            expires_delta=access_token_expires,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def logout_user(self, user_id: str) -> bool:
        """Logout user by invalidating refresh token"""
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            return False

        user.refresh_token = None
        self.db.commit()
        return True

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            return False

        if not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User registered via OAuth, cannot change password",
            )

        if not self.verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # Hash new password
        user.password_hash = self.get_password_hash(new_password)

        # Invalidate refresh token to force re-login
        user.refresh_token = None

        self.db.commit()
        return True
