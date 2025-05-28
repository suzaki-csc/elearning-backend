"""
Learning progress API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.api.v1.deps import get_current_user, get_current_active_admin
from src.models.user import User
from src.models.content import Content
from src.models.learning import LearningPathContent
from src.services.learning_service import LearningService
from src.schemas.learning import (
    ProgressUpdate,
    LearningProgressResponse,
    UserProgressSummary,
    ContentProgressStats,
    AssignmentCreate,
    AssignmentResponse,
    LearningPathCreate,
    LearningPathResponse,
    LearningPathProgress,
    ProgressListResponse,
    AssignmentListResponse,
)

router = APIRouter()


@router.post("/progress/{content_id}")
def update_progress(
    content_id: str,
    progress_data: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user progress for content"""
    learning_service = LearningService(db)

    try:
        progress = learning_service.update_progress(
            current_user.user_id, content_id, progress_data
        )

        return {
            "message": "Progress updated successfully",
            "progress_id": progress.progress_id,
            "progress_percentage": progress.progress_percentage,
            "is_completed": progress.is_completed,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/progress/{content_id}")
def get_content_progress(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user progress for specific content"""
    learning_service = LearningService(db)

    progress = learning_service.get_user_progress(current_user.user_id, content_id)

    if not progress:
        return {
            "progress_percentage": 0.0,
            "time_spent_minutes": 0,
            "is_completed": False,
            "started_at": None,
        }

    return {
        "progress_percentage": progress.progress_percentage,
        "time_spent_minutes": progress.time_spent_minutes,
        "is_completed": progress.is_completed,
        "started_at": progress.started_at,
        "completed_at": progress.completed_at,
        "last_accessed_at": progress.last_accessed_at,
    }


@router.get("/progress")
def get_user_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all user progress"""
    learning_service = LearningService(db)

    progress_list = learning_service.get_user_progress(current_user.user_id)

    # Convert to response format with content info
    progress_responses = []
    for progress in progress_list:
        # Get content info
        content = (
            db.query(Content).filter(Content.content_id == progress.content_id).first()
        )

        if content:
            progress_responses.append(
                {
                    "progress_id": progress.progress_id,
                    "user_id": progress.user_id,
                    "content_id": progress.content_id,
                    "content_title": content.title,
                    "progress_percentage": progress.progress_percentage,
                    "time_spent_minutes": progress.time_spent_minutes,
                    "is_completed": progress.is_completed,
                    "started_at": progress.started_at,
                    "completed_at": progress.completed_at,
                    "last_accessed_at": progress.last_accessed_at,
                }
            )

    return {"progress": progress_responses}


@router.get("/summary")
def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user progress summary"""
    learning_service = LearningService(db)

    summary = learning_service.get_user_progress_summary(current_user.user_id)
    return summary


@router.get("/stats/content/{content_id}")
def get_content_stats(
    content_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Get progress statistics for content (admin only)"""
    learning_service = LearningService(db)

    stats = learning_service.get_content_progress_stats(content_id)

    if not stats:
        raise HTTPException(status_code=404, detail="Content not found")

    return stats


@router.post("/assignments")
def create_assignment(
    assignment_data: AssignmentCreate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Create learning assignment (admin only)"""
    learning_service = LearningService(db)

    try:
        assignment = learning_service.create_assignment(
            assignment_data, current_user.user_id
        )

        # Get user and content info for response
        user = db.query(User).filter(User.user_id == assignment.user_id).first()
        content = (
            db.query(Content)
            .filter(Content.content_id == assignment.content_id)
            .first()
        )

        return {
            "assignment_id": assignment.assignment_id,
            "user_id": assignment.user_id,
            "user_name": user.display_name if user else "Unknown",
            "content_id": assignment.content_id,
            "content_title": content.title if content else "Unknown",
            "assigned_by": assignment.assigned_by,
            "assigned_at": assignment.assigned_at,
            "due_date": assignment.due_date,
            "is_mandatory": assignment.is_mandatory,
            "notes": assignment.notes,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/assignments")
def get_user_assignments(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user assignments with pagination"""
    learning_service = LearningService(db)

    skip = (page - 1) * per_page
    assignments, total = learning_service.get_user_assignments(
        current_user.user_id, skip, per_page
    )

    # Convert to response format
    assignment_responses = []
    for assignment in assignments:
        # Get content and progress info
        content = (
            db.query(Content)
            .filter(Content.content_id == assignment.content_id)
            .first()
        )

        progress = learning_service.get_user_progress(
            current_user.user_id, assignment.content_id
        )

        assignment_responses.append(
            {
                "assignment_id": assignment.assignment_id,
                "user_id": assignment.user_id,
                "user_name": current_user.display_name,
                "content_id": assignment.content_id,
                "content_title": content.title if content else "Unknown",
                "assigned_by": assignment.assigned_by,
                "assigned_at": assignment.assigned_at,
                "due_date": assignment.due_date,
                "is_mandatory": assignment.is_mandatory,
                "notes": assignment.notes,
                "progress_percentage": progress.progress_percentage
                if progress
                else 0.0,
                "is_completed": progress.is_completed if progress else False,
            }
        )

    total_pages = (total + per_page - 1) // per_page

    return {
        "assignments": assignment_responses,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.post("/paths")
def create_learning_path(
    path_data: LearningPathCreate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Create learning path (admin only)"""
    learning_service = LearningService(db)

    try:
        path = learning_service.create_learning_path(path_data, current_user.user_id)

        # Get contents info
        contents = []
        for content_id in path_data.content_ids:
            content = db.query(Content).filter(Content.content_id == content_id).first()
            if content:
                contents.append(
                    {
                        "content_id": content.content_id,
                        "title": content.title,
                        "content_type": content.content_type,
                        "duration_minutes": content.duration_minutes,
                    }
                )

        return {
            "path_id": path.path_id,
            "title": path.title,
            "description": path.description,
            "created_by": path.created_by,
            "is_active": path.is_active,
            "created_at": path.created_at,
            "contents": contents,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/paths")
def get_learning_paths(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get learning paths with pagination"""
    learning_service = LearningService(db)

    skip = (page - 1) * per_page
    paths, total = learning_service.get_learning_paths(skip, per_page)

    # Convert to response format
    path_responses = []
    for path in paths:
        # Get path contents
        path_contents = (
            db.query(LearningPathContent)
            .filter(LearningPathContent.path_id == path.path_id)
            .order_by(LearningPathContent.order_index)
            .all()
        )

        contents = []
        for path_content in path_contents:
            content = (
                db.query(Content)
                .filter(Content.content_id == path_content.content_id)
                .first()
            )
            if content:
                contents.append(
                    {
                        "content_id": content.content_id,
                        "title": content.title,
                        "content_type": content.content_type,
                        "order_index": path_content.order_index,
                        "is_required": path_content.is_required,
                    }
                )

        path_responses.append(
            {
                "path_id": path.path_id,
                "title": path.title,
                "description": path.description,
                "created_by": path.created_by,
                "is_active": path.is_active,
                "created_at": path.created_at,
                "contents": contents,
            }
        )

    total_pages = (total + per_page - 1) // per_page

    return {
        "paths": path_responses,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/paths/{path_id}/progress")
def get_learning_path_progress(
    path_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user progress for learning path"""
    learning_service = LearningService(db)

    progress = learning_service.get_learning_path_progress(
        current_user.user_id, path_id
    )

    if not progress:
        raise HTTPException(status_code=404, detail="Learning path not found")

    return progress
