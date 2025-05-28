"""
API v1 router
"""

from fastapi import APIRouter
from src.api.v1 import users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])

# TODO: Add other routers
# api_router.include_router(contents.router, prefix="/contents", tags=["contents"])
# api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
