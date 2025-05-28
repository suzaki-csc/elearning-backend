"""
Learning service for managing user progress and analytics
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.learning import (
    LearningProgress,
    LearningAssignment,
    LearningPath,
    LearningPathContent,
)
from src.models.content import Content
from src.schemas.learning import (
    ProgressUpdate,
    AssignmentCreate,
    LearningPathCreate,
)


class LearningService:
    """Service for learning progress management"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_progress(
        self, user_id: str, content_id: str = None
    ) -> Optional[LearningProgress]:
        """Get user learning progress for specific content or all"""
        query = self.db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id
        )

        if content_id:
            query = query.filter(LearningProgress.content_id == content_id)
            return query.first()

        return query.all()

    def update_progress(
        self, user_id: str, content_id: str, progress_data: ProgressUpdate
    ) -> LearningProgress:
        """Update user progress for content"""
        # Get or create progress record
        progress = (
            self.db.query(LearningProgress)
            .filter(
                and_(
                    LearningProgress.user_id == user_id,
                    LearningProgress.content_id == content_id,
                )
            )
            .first()
        )

        if not progress:
            progress = LearningProgress(
                progress_id=str(uuid.uuid4()),
                user_id=user_id,
                content_id=content_id,
                progress_percentage=0.0,
                time_spent_minutes=0,
                is_completed=False,
                started_at=datetime.utcnow(),
            )
            self.db.add(progress)

        # Update progress
        progress.progress_percentage = progress_data.progress_percentage
        progress.time_spent_minutes += progress_data.time_spent_minutes
        progress.last_accessed_at = datetime.utcnow()

        # Mark as completed if 100%
        if progress_data.progress_percentage >= 100.0 and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(progress)
        return progress

    def get_user_progress_summary(self, user_id: str) -> dict:
        """Get user progress summary statistics"""
        # Get all progress records for user
        progress_records = (
            self.db.query(LearningProgress)
            .filter(LearningProgress.user_id == user_id)
            .all()
        )

        total_contents = len(progress_records)
        completed_contents = sum(1 for p in progress_records if p.is_completed)
        in_progress_contents = total_contents - completed_contents
        total_time_spent = sum(p.time_spent_minutes for p in progress_records)
        completion_rate = (
            (completed_contents / total_contents * 100) if total_contents > 0 else 0
        )

        return {
            "user_id": user_id,
            "total_contents": total_contents,
            "completed_contents": completed_contents,
            "in_progress_contents": in_progress_contents,
            "total_time_spent_minutes": total_time_spent,
            "completion_rate": round(completion_rate, 2),
        }

    def get_content_progress_stats(self, content_id: str) -> dict:
        """Get progress statistics for specific content"""
        # Get all progress records for content
        progress_records = (
            self.db.query(LearningProgress)
            .filter(LearningProgress.content_id == content_id)
            .all()
        )

        # Get content info
        content = (
            self.db.query(Content).filter(Content.content_id == content_id).first()
        )
        if not content:
            return None

        total_users = len(progress_records)
        completed_users = sum(1 for p in progress_records if p.is_completed)
        average_progress = (
            sum(p.progress_percentage for p in progress_records) / total_users
            if total_users > 0
            else 0
        )
        average_time_spent = (
            sum(p.time_spent_minutes for p in progress_records) / total_users
            if total_users > 0
            else 0
        )
        completion_rate = (
            (completed_users / total_users * 100) if total_users > 0 else 0
        )

        return {
            "content_id": content_id,
            "content_title": content.title,
            "total_users": total_users,
            "completed_users": completed_users,
            "average_progress": round(average_progress, 2),
            "average_time_spent": round(average_time_spent),
            "completion_rate": round(completion_rate, 2),
        }

    def create_assignment(
        self, assignment_data: AssignmentCreate, assigned_by: str
    ) -> LearningAssignment:
        """Create learning assignment"""
        assignment = LearningAssignment(
            assignment_id=str(uuid.uuid4()),
            user_id=assignment_data.user_id,
            content_id=assignment_data.content_id,
            assigned_by=assigned_by,
            due_date=assignment_data.due_date,
            is_mandatory=assignment_data.is_mandatory,
            notes=assignment_data.notes,
        )

        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def get_user_assignments(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[List[LearningAssignment], int]:
        """Get assignments for user with pagination"""
        query = self.db.query(LearningAssignment).filter(
            LearningAssignment.user_id == user_id
        )

        total = query.count()
        assignments = query.offset(skip).limit(limit).all()

        return assignments, total

    def create_learning_path(
        self, path_data: LearningPathCreate, created_by: str
    ) -> LearningPath:
        """Create learning path with contents"""
        # Create learning path
        path = LearningPath(
            path_id=str(uuid.uuid4()),
            title=path_data.title,
            description=path_data.description,
            created_by=created_by,
        )

        self.db.add(path)
        self.db.flush()  # Get the path_id

        # Add contents to path
        for index, content_id in enumerate(path_data.content_ids):
            path_content = LearningPathContent(
                path_content_id=str(uuid.uuid4()),
                path_id=path.path_id,
                content_id=content_id,
                order_index=index,
                is_required=True,
            )
            self.db.add(path_content)

        self.db.commit()
        self.db.refresh(path)
        return path

    def get_learning_paths(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[List[LearningPath], int]:
        """Get learning paths with pagination"""
        query = self.db.query(LearningPath).filter(LearningPath.is_active)

        total = query.count()
        paths = query.offset(skip).limit(limit).all()

        return paths, total

    def get_learning_path_progress(self, user_id: str, path_id: str) -> dict:
        """Get user progress for learning path"""
        # Get path contents
        path_contents = (
            self.db.query(LearningPathContent)
            .filter(LearningPathContent.path_id == path_id)
            .order_by(LearningPathContent.order_index)
            .all()
        )

        # Get path info
        path = (
            self.db.query(LearningPath).filter(LearningPath.path_id == path_id).first()
        )
        if not path:
            return None

        total_contents = len(path_contents)
        completed_contents = 0

        # Check progress for each content
        for path_content in path_contents:
            progress = (
                self.db.query(LearningProgress)
                .filter(
                    and_(
                        LearningProgress.user_id == user_id,
                        LearningProgress.content_id == path_content.content_id,
                        LearningProgress.is_completed,
                    )
                )
                .first()
            )
            if progress:
                completed_contents += 1

        progress_percentage = (
            (completed_contents / total_contents * 100) if total_contents > 0 else 0
        )

        # Estimate remaining time (simplified)
        remaining_contents = total_contents - completed_contents
        estimated_time_remaining = remaining_contents * 30  # Assume 30 min per content

        return {
            "path_id": path_id,
            "path_title": path.title,
            "total_contents": total_contents,
            "completed_contents": completed_contents,
            "progress_percentage": round(progress_percentage, 2),
            "estimated_time_remaining": estimated_time_remaining,
        }
