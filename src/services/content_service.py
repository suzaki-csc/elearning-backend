"""
Content service layer (placeholder)
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from src.models.content import Content


class ContentService:
    """Content service class (placeholder)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_contents(self, skip: int = 0, limit: int = 100) -> List[Content]:
        """Get all contents with pagination"""
        return self.db.query(Content).offset(skip).limit(limit).all()
    
    async def get_content_by_id(self, content_id: str) -> Optional[Content]:
        """Get content by ID"""
        return self.db.query(Content).filter(Content.content_id == content_id)