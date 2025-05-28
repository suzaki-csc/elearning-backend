"""
Learning management models (placeholder)
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from src.models.base import BaseModel


class LearningAssignment(BaseModel):
    """Learning assignment model (placeholder)"""

    __tablename__ = "learning_assignments"

    assignment_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"))
    content_id = Column(String(36), ForeignKey("contents.content_id"))
    status = Column(String(20), nullable=False, default="not_started")
    due_date = Column(DateTime)
    completed_at = Column(DateTime)


class LearningProgress(BaseModel):
    """Learning progress model (placeholder)"""

    __tablename__ = "learning_progress"

    progress_id = Column(String(36), primary_key=True, index=True)
    assignment_id = Column(String(36), ForeignKey("learning_assignments.assignment_id"))
    progress_percentage = Column(Integer, default=0)
    last_accessed_at = Column(DateTime)
