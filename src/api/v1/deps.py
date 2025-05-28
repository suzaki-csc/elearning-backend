"""
Dependency injection for FastAPI
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.user import User
from src.services.auth_service import AuthService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    auth_service = AuthService(db)
    token_data = auth_service.verify_token(credentials.credentials)
    
    if token_data is None or token_data.user_id is None:
        raise credentials_exception
    
    user = await auth_service.user_service.get_user_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active admin user
    TODO: Implement proper role-based access control
    For now, all authenticated users are considered admins
    """
    return current_user


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user if token is provided, otherwise return None
    Useful for endpoints that work for both authenticated and anonymous users
    """
    if credentials is None:
        return None
    
    try:
        auth_service = AuthService(db)
        token_data = auth_service.verify_token(credentials.credentials)
        
        if token_data is None or token_data.user_id is None:
            return None
        
        user = await auth_service.user_service.get_user_by_id(token_data.user_id)
        if user is None or not user.is_active:
            return None
        
        return user
    except Exception:
        return None