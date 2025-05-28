"""
Assessment and quiz API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.api.v1.deps import get_current_user, get_current_active_admin
from src.models.user import User
from src.models.assessment import Question, QuestionChoice
from src.services.assessment_service import AssessmentService
from src.schemas.assessment import (
    QuizCreate,
    QuizUpdate,
    QuizResponse,
    QuizAttemptSubmit,
    QuizAttemptResponse,
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentResponse,
    AssessmentSubmissionCreate,
    AssessmentSubmissionGrade,
    AssessmentSubmissionResponse,
    QuizListResponse,
    AssessmentListResponse,
    QuizAttemptListResponse,
    AssessmentSubmissionListResponse,
    QuizStatistics,
    UserQuizStatistics,
    QuestionResponse,
    QuestionChoiceResponse,
)

router = APIRouter()


# Quiz Management Endpoints
@router.post("/quizzes", response_model=QuizResponse)
def create_quiz(
    quiz_data: QuizCreate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Create a new quiz (admin only)"""
    assessment_service = AssessmentService(db)

    try:
        quiz = assessment_service.create_quiz(quiz_data, current_user.user_id)
        
        # Convert to response format
        questions = []
        for question in quiz.questions:
            choices = []
            for choice in question.choices:
                choices.append(QuestionChoiceResponse(
                    choice_id=choice.choice_id,
                    choice_text=choice.choice_text,
                    is_correct=choice.is_correct,
                    order_index=choice.order_index,
                ))
            
            questions.append(QuestionResponse(
                question_id=question.question_id,
                question_text=question.question_text,
                question_type=question.question_type,
                points=question.points,
                order_index=question.order_index,
                explanation=question.explanation,
                is_required=question.is_required,
                choices=choices,
            ))

        return QuizResponse(
            quiz_id=quiz.quiz_id,
            title=quiz.title,
            description=quiz.description,
            content_id=quiz.content_id,
            time_limit_minutes=quiz.time_limit_minutes,
            max_attempts=quiz.max_attempts,
            passing_score=quiz.passing_score,
            is_randomized=quiz.is_randomized,
            is_published=quiz.is_published,
            created_by=quiz.created_by,
            created_at=quiz.created_at,
            updated_at=quiz.updated_at,
            questions=questions,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/quizzes", response_model=QuizListResponse)
def get_quizzes(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    content_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get quizzes with pagination"""
    assessment_service = AssessmentService(db)

    skip = (page - 1) * per_page
    quizzes, total = assessment_service.get_quizzes(skip, per_page, content_id)

    # Convert to response format
    quiz_responses = []
    for quiz in quizzes:
        quiz_responses.append(QuizResponse(
            quiz_id=quiz.quiz_id,
            title=quiz.title,
            description=quiz.description,
            content_id=quiz.content_id,
            time_limit_minutes=quiz.time_limit_minutes,
            max_attempts=quiz.max_attempts,
            passing_score=quiz.passing_score,
            is_randomized=quiz.is_randomized,
            is_published=quiz.is_published,
            created_by=quiz.created_by,
            created_at=quiz.created_at,
            updated_at=quiz.updated_at,
            questions=[],  # Don't include questions in list view
        ))

    total_pages = (total + per_page - 1) // per_page

    return QuizListResponse(
        quizzes=quiz_responses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
def get_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get quiz by ID with questions"""
    assessment_service = AssessmentService(db)

    quiz = assessment_service.get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Get questions and choices
    questions = []
    for question in quiz.questions:
        choices = []
        for choice in question.choices:
            # Hide correct answers for non-admin users
            show_correct = current_user.is_admin if hasattr(current_user, 'is_admin') else False
            choices.append(QuestionChoiceResponse(
                choice_id=choice.choice_id,
                choice_text=choice.choice_text,
                is_correct=choice.is_correct if show_correct else False,
                order_index=choice.order_index,
            ))
        
        questions.append(QuestionResponse(
            question_id=question.question_id,
            question_text=question.question_text,
            question_type=question.question_type,
            points=question.points,
            order_index=question.order_index,
            explanation=question.explanation if show_correct else None,
            is_required=question.is_required,
            choices=choices,
        ))

    return QuizResponse(
        quiz_id=quiz.quiz_id,
        title=quiz.title,
        description=quiz.description,
        content_id=quiz.content_id,
        time_limit_minutes=quiz.time_limit_minutes,
        max_attempts=quiz.max_attempts,
        passing_score=quiz.passing_score,
        is_randomized=quiz.is_randomized,
        is_published=quiz.is_published,
        created_by=quiz.created_by,
        created_at=quiz.created_at,
        updated_at=quiz.updated_at,
        questions=questions,
    )


@router.put("/quizzes/{quiz_id}", response_model=QuizResponse)
def update_quiz(
    quiz_id: str,
    quiz_data: QuizUpdate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Update quiz (admin only)"""
    assessment_service = AssessmentService(db)

    quiz = assessment_service.update_quiz(quiz_id, quiz_data)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return QuizResponse(
        quiz_id=quiz.quiz_id,
        title=quiz.title,
        description=quiz.description,
        content_id=quiz.content_id,
        time_limit_minutes=quiz.time_limit_minutes,
        max_attempts=quiz.max_attempts,
        passing_score=quiz.passing_score,
        is_randomized=quiz.is_randomized,
        is_published=quiz.is_published,
        created_by=quiz.created_by,
        created_at=quiz.created_at,
        updated_at=quiz.updated_at,
        questions=[],
    )


@router.delete("/quizzes/{quiz_id}")
def delete_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Delete quiz (admin only)"""
    assessment_service = AssessmentService(db)

    success = assessment_service.delete_quiz(quiz_id)
    if not success:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return {"message": "Quiz deleted successfully"}


@router.post("/quizzes/{quiz_id}/publish")
def publish_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Publish quiz (admin only)"""
    assessment_service = AssessmentService(db)

    quiz = assessment_service.publish_quiz(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return {"message": "Quiz published successfully", "quiz_id": quiz_id}


# Quiz Attempt Endpoints
@router.post("/quizzes/{quiz_id}/attempts", response_model=QuizAttemptResponse)
def start_quiz_attempt(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a new quiz attempt"""
    assessment_service = AssessmentService(db)

    attempt = assessment_service.start_quiz_attempt(quiz_id, current_user.user_id)
    if not attempt:
        raise HTTPException(
            status_code=400, 
            detail="Cannot start quiz attempt. Quiz may not be published or attempt limit reached."
        )

    return QuizAttemptResponse(
        attempt_id=attempt.attempt_id,
        quiz_id=attempt.quiz_id,
        user_id=attempt.user_id,
        attempt_number=attempt.attempt_number,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        time_spent_minutes=attempt.time_spent_minutes,
        score=attempt.score,
        max_score=attempt.max_score,
        is_passed=attempt.is_passed,
        status=attempt.status,
        answers=[],
    )


@router.post("/attempts/{attempt_id}/submit", response_model=QuizAttemptResponse)
def submit_quiz_attempt(
    attempt_id: str,
    submission: QuizAttemptSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit quiz attempt with answers"""
    assessment_service = AssessmentService(db)

    attempt = assessment_service.submit_quiz_attempt(attempt_id, submission)
    if not attempt:
        raise HTTPException(
            status_code=400, 
            detail="Cannot submit quiz attempt. Attempt may not exist or already completed."
        )

    # Get answers for response
    answer_responses = []
    for answer in attempt.answers:
        answer_responses.append({
            "answer_id": answer.answer_id,
            "question_id": answer.question_id,
            "selected_choices": answer.selected_choices,
            "text_answer": answer.text_answer,
            "is_correct": answer.is_correct,
            "points_earned": answer.points_earned,
            "answered_at": answer.answered_at,
        })

    return QuizAttemptResponse(
        attempt_id=attempt.attempt_id,
        quiz_id=attempt.quiz_id,
        user_id=attempt.user_id,
        attempt_number=attempt.attempt_number,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        time_spent_minutes=attempt.time_spent_minutes,
        score=attempt.score,
        max_score=attempt.max_score,
        is_passed=attempt.is_passed,
        status=attempt.status,
        answers=answer_responses,
    )


@router.get("/attempts", response_model=QuizAttemptListResponse)
def get_quiz_attempts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    quiz_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's quiz attempts"""
    assessment_service = AssessmentService(db)

    skip = (page - 1) * per_page
    attempts, total = assessment_service.get_quiz_attempts(
        quiz_id=quiz_id, user_id=current_user.user_id, skip=skip, limit=per_page
    )

    # Convert to response format
    attempt_responses = []
    for attempt in attempts:
        attempt_responses.append(QuizAttemptResponse(
            attempt_id=attempt.attempt_id,
            quiz_id=attempt.quiz_id,
            user_id=attempt.user_id,
            attempt_number=attempt.attempt_number,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            time_spent_minutes=attempt.time_spent_minutes,
            score=attempt.score,
            max_score=attempt.max_score,
            is_passed=attempt.is_passed,
            status=attempt.status,
            answers=[],  # Don't include answers in list view
        ))

    total_pages = (total + per_page - 1) // per_page

    return QuizAttemptListResponse(
        attempts=attempt_responses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


# Assessment Management Endpoints
@router.post("/assessments", response_model=AssessmentResponse)
def create_assessment(
    assessment_data: AssessmentCreate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Create a new assessment (admin only)"""
    assessment_service = AssessmentService(db)

    try:
        assessment = assessment_service.create_assessment(assessment_data, current_user.user_id)
        
        return AssessmentResponse(
            assessment_id=assessment.assessment_id,
            title=assessment.title,
            description=assessment.description,
            assessment_type=assessment.assessment_type,
            content_id=assessment.content_id,
            due_date=assessment.due_date,
            total_points=assessment.total_points,
            passing_score=assessment.passing_score,
            is_published=assessment.is_published,
            created_by=assessment.created_by,
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/assessments", response_model=AssessmentListResponse)
def get_assessments(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    content_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get assessments with pagination"""
    assessment_service = AssessmentService(db)

    skip = (page - 1) * per_page
    assessments, total = assessment_service.get_assessments(skip, per_page, content_id)

    # Convert to response format
    assessment_responses = []
    for assessment in assessments:
        assessment_responses.append(AssessmentResponse(
            assessment_id=assessment.assessment_id,
            title=assessment.title,
            description=assessment.description,
            assessment_type=assessment.assessment_type,
            content_id=assessment.content_id,
            due_date=assessment.due_date,
            total_points=assessment.total_points,
            passing_score=assessment.passing_score,
            is_published=assessment.is_published,
            created_by=assessment.created_by,
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
        ))

    total_pages = (total + per_page - 1) // per_page

    return AssessmentListResponse(
        assessments=assessment_responses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/assessments/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get assessment by ID"""
    assessment_service = AssessmentService(db)

    assessment = assessment_service.get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return AssessmentResponse(
        assessment_id=assessment.assessment_id,
        title=assessment.title,
        description=assessment.description,
        assessment_type=assessment.assessment_type,
        content_id=assessment.content_id,
        due_date=assessment.due_date,
        total_points=assessment.total_points,
        passing_score=assessment.passing_score,
        is_published=assessment.is_published,
        created_by=assessment.created_by,
        created_at=assessment.created_at,
        updated_at=assessment.updated_at,
    )


@router.put("/assessments/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(
    assessment_id: str,
    assessment_data: AssessmentUpdate,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Update assessment (admin only)"""
    assessment_service = AssessmentService(db)

    assessment = assessment_service.update_assessment(assessment_id, assessment_data)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return AssessmentResponse(
        assessment_id=assessment.assessment_id,
        title=assessment.title,
        description=assessment.description,
        assessment_type=assessment.assessment_type,
        content_id=assessment.content_id,
        due_date=assessment.due_date,
        total_points=assessment.total_points,
        passing_score=assessment.passing_score,
        is_published=assessment.is_published,
        created_by=assessment.created_by,
        created_at=assessment.created_at,
        updated_at=assessment.updated_at,
    )


@router.delete("/assessments/{assessment_id}")
def delete_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Delete assessment (admin only)"""
    assessment_service = AssessmentService(db)

    success = assessment_service.delete_assessment(assessment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {"message": "Assessment deleted successfully"}


@router.post("/assessments/{assessment_id}/publish")
def publish_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Publish assessment (admin only)"""
    assessment_service = AssessmentService(db)

    assessment = assessment_service.publish_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {"message": "Assessment published successfully", "assessment_id": assessment_id}


# Assessment Submission Endpoints
@router.post("/assessments/{assessment_id}/submissions", response_model=AssessmentSubmissionResponse)
def submit_assessment(
    assessment_id: str,
    submission_data: AssessmentSubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit assessment"""
    assessment_service = AssessmentService(db)

    submission = assessment_service.submit_assessment(
        assessment_id, current_user.user_id, submission_data
    )
    if not submission:
        raise HTTPException(
            status_code=400, 
            detail="Cannot submit assessment. Assessment may not be published."
        )

    return AssessmentSubmissionResponse(
        submission_id=submission.submission_id,
        assessment_id=submission.assessment_id,
        user_id=submission.user_id,
        submission_data=submission.submission_data,
        file_path=submission.file_path,
        score=submission.score,
        feedback=submission.feedback,
        graded_by=submission.graded_by,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at,
        status=submission.status,
    )


@router.post("/submissions/{submission_id}/grade", response_model=AssessmentSubmissionResponse)
def grade_submission(
    submission_id: str,
    grade_data: AssessmentSubmissionGrade,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Grade assessment submission (admin only)"""
    assessment_service = AssessmentService(db)

    submission = assessment_service.grade_submission(
        submission_id, grade_data, current_user.user_id
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return AssessmentSubmissionResponse(
        submission_id=submission.submission_id,
        assessment_id=submission.assessment_id,
        user_id=submission.user_id,
        submission_data=submission.submission_data,
        file_path=submission.file_path,
        score=submission.score,
        feedback=submission.feedback,
        graded_by=submission.graded_by,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at,
        status=submission.status,
    )


@router.get("/submissions", response_model=AssessmentSubmissionListResponse)
def get_assessment_submissions(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    assessment_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's assessment submissions"""
    assessment_service = AssessmentService(db)

    skip = (page - 1) * per_page
    submissions, total = assessment_service.get_assessment_submissions(
        assessment_id=assessment_id, user_id=current_user.user_id, skip=skip, limit=per_page
    )

    # Convert to response format
    submission_responses = []
    for submission in submissions:
        submission_responses.append(AssessmentSubmissionResponse(
            submission_id=submission.submission_id,
            assessment_id=submission.assessment_id,
            user_id=submission.user_id,
            submission_data=submission.submission_data,
            file_path=submission.file_path,
            score=submission.score,
            feedback=submission.feedback,
            graded_by=submission.graded_by,
            submitted_at=submission.submitted_at,
            graded_at=submission.graded_at,
            status=submission.status,
        ))

    total_pages = (total + per_page - 1) // per_page

    return AssessmentSubmissionListResponse(
        submissions=submission_responses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


# Statistics Endpoints
@router.get("/quizzes/{quiz_id}/statistics", response_model=QuizStatistics)
def get_quiz_statistics(
    quiz_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Get quiz statistics (admin only)"""
    assessment_service = AssessmentService(db)

    stats = assessment_service.get_quiz_statistics(quiz_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return QuizStatistics(**stats)


@router.get("/users/{user_id}/quiz-statistics", response_model=UserQuizStatistics)
def get_user_quiz_statistics(
    user_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
):
    """Get user quiz statistics (admin only)"""
    assessment_service = AssessmentService(db)

    stats = assessment_service.get_user_quiz_statistics(user_id)
    return UserQuizStatistics(**stats)


@router.get("/my-quiz-statistics", response_model=UserQuizStatistics)
def get_my_quiz_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's quiz statistics"""
    assessment_service = AssessmentService(db)

    stats = assessment_service.get_user_quiz_statistics(current_user.user_id)
    return UserQuizStatistics(**stats) 