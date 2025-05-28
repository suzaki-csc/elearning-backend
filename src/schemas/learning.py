"""
Learning schemas (placeholder)
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LearningAssignmentBase(BaseModel):
    """Base learning assignment schema"""
    user_id: str
    content_id: str
    due_date: Optional[datetime] = None


class LearningAssignmentCreate(LearningAssignmentBase):
    """Learning assignment creation schema"""
    pass


class LearningAssignmentResponse(LearningAssignmentBase):
    """Learning assignment response schema"""
    assignment_id: str
    status: str
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True