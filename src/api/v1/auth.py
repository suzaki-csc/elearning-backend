"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.api.v1.deps import get_current_user
from src.models.user import User
from src.services.auth_service import AuthService
from src.schemas.auth import (
    LoginRequest, TokenResponse, UserRegistration, 
    PasswordChangeRequest, RefreshTokenRequest
)
from src.schemas.user import UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegistration,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login user and return access token"""
    auth_service = AuthService(db)
    tokens = await auth_service.login_user(
        email=login_data.email,
        password=login_data.password
    )
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_access_token(refresh_data.refresh_token)
    return TokenResponse(
        access_token=tokens["access_token"],
        expires_in=tokens["expires_in"]
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user by invalidating refresh token"""
    auth_service = AuthService(db)
    success = await auth_service.logout_user(current_user.user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )
    
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    auth_service = AuthService(db)
    success = await auth_service.change_password(
        user_id=current_user.user_id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password change failed"
        )
    
    return {"message": "Password changed successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """Verify if the provided token is valid"""
    return {
        "valid": True,
        "user_id": current_user.user_id,
        "email": current_user.email
    } 