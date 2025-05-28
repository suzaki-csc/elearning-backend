"""
Learning progress models
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.models.base import Base


class LearningProgress(Base):
    """User learning progress for content"""

    __tablename__ = "learning_progress"

    progress_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    content_id = Column(String(36), ForeignKey("contents.content_id"), nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    time_spent_minutes = Column(Integer, default=0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="learning_progress")
    content = relationship("Content", back_populates="learning_progress")


class LearningAssignment(Base):
    """Learning assignments for users"""

    __tablename__ = "learning_assignments"

    assignment_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    content_id = Column(String(36), ForeignKey("contents.content_id"), nullable=False)
    assigned_by = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=True)
    is_mandatory = Column(Boolean, default=False, nullable=False)
    notes = Column(String(500), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    content = relationship("Content")
    assigner = relationship("User", foreign_keys=[assigned_by])


class LearningPath(Base):
    """Learning paths containing multiple contents"""

    __tablename__ = "learning_paths"

    path_id = Column(String(36), primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    created_by = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User")


class LearningPathContent(Base):
    """Contents in learning paths with order"""

    __tablename__ = "learning_path_contents"

    path_content_id = Column(String(36), primary_key=True)
    path_id = Column(String(36), ForeignKey("learning_paths.path_id"), nullable=False)
    content_id = Column(String(36), ForeignKey("contents.content_id"), nullable=False)
    order_index = Column(Integer, nullable=False)
    is_required = Column(Boolean, default=True, nullable=False)

    # Relationships
    path = relationship("LearningPath")
    content = relationship("Content")
