"""
Learning service layer (placeholder)
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from src.models.learning import LearningAssignment


class LearningService:
    """Learning service class (placeholder)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_assignments(self, user_id: str) -> List[LearningAssignment]:
        """Get user assignments"""
        return self.db.query(LearningAssignment).filter(
            LearningAssignment.user_id == user_id
        ).all()