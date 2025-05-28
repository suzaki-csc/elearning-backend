"""
Learning progress schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ProgressUpdate(BaseModel):
    """Progress update request"""

    progress_percentage: float = Field(..., ge=0.0, le=100.0)
    time_spent_minutes: int = Field(..., ge=0)


class LearningProgressResponse(BaseModel):
    """Learning progress response"""

    progress_id: str
    user_id: str
    content_id: str
    content_title: str
    progress_percentage: float
    time_spent_minutes: int
    is_completed: bool
    started_at: datetime
    completed_at: Optional[datetime]
    last_accessed_at: datetime


class UserProgressSummary(BaseModel):
    """User progress summary"""

    user_id: str
    total_contents: int
    completed_contents: int
    in_progress_contents: int
    total_time_spent_minutes: int
    completion_rate: float


class ContentProgressStats(BaseModel):
    """Content progress statistics"""

    content_id: str
    content_title: str
    total_users: int
    completed_users: int
    average_progress: float
    average_time_spent: int
    completion_rate: float


class AssignmentCreate(BaseModel):
    """Assignment creation request"""

    user_id: str
    content_id: str
    due_date: Optional[datetime] = None
    is_mandatory: bool = False
    notes: Optional[str] = Field(None, max_length=500)


class AssignmentResponse(BaseModel):
    """Assignment response"""

    assignment_id: str
    user_id: str
    user_name: str
    content_id: str
    content_title: str
    assigned_by: str
    assigned_at: datetime
    due_date: Optional[datetime]
    is_mandatory: bool
    notes: Optional[str]
    progress_percentage: Optional[float] = None
    is_completed: Optional[bool] = None


class LearningPathCreate(BaseModel):
    """Learning path creation request"""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    content_ids: List[str] = Field(..., min_items=1)


class LearningPathResponse(BaseModel):
    """Learning path response"""

    path_id: str
    title: str
    description: Optional[str]
    created_by: str
    is_active: bool
    created_at: datetime
    contents: List[dict]  # Content info with order


class LearningPathProgress(BaseModel):
    """Learning path progress"""

    path_id: str
    path_title: str
    total_contents: int
    completed_contents: int
    progress_percentage: float
    estimated_time_remaining: int


class ProgressListResponse(BaseModel):
    """Progress list response with pagination"""

    progress: List[LearningProgressResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class AssignmentListResponse(BaseModel):
    """Assignment list response with pagination"""

    assignments: List[AssignmentResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
