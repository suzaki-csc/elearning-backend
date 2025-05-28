"""
Assessment and quiz schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class QuestionType(str, Enum):
    """Question type enumeration"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class AssessmentType(str, Enum):
    """Assessment type enumeration"""
    QUIZ = "quiz"
    EXAM = "exam"
    ASSIGNMENT = "assignment"
    PROJECT = "project"


class AttemptStatus(str, Enum):
    """Quiz attempt status enumeration"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SubmissionStatus(str, Enum):
    """Assessment submission status enumeration"""
    SUBMITTED = "submitted"
    GRADED = "graded"
    RETURNED = "returned"


# Question Choice Schemas
class QuestionChoiceCreate(BaseModel):
    """Question choice creation schema"""
    choice_text: str = Field(..., min_length=1, max_length=1000)
    is_correct: bool = False
    order_index: int = Field(..., ge=0)


class QuestionChoiceResponse(BaseModel):
    """Question choice response schema"""
    choice_id: str
    choice_text: str
    is_correct: bool
    order_index: int


# Question Schemas
class QuestionCreate(BaseModel):
    """Question creation schema"""
    question_text: str = Field(..., min_length=1, max_length=2000)
    question_type: QuestionType
    points: float = Field(1.0, ge=0.1, le=100.0)
    order_index: int = Field(..., ge=0)
    explanation: Optional[str] = Field(None, max_length=1000)
    is_required: bool = True
    choices: List[QuestionChoiceCreate] = []


class QuestionResponse(BaseModel):
    """Question response schema"""
    question_id: str
    question_text: str
    question_type: QuestionType
    points: float
    order_index: int
    explanation: Optional[str]
    is_required: bool
    choices: List[QuestionChoiceResponse] = []


# Quiz Schemas
class QuizCreate(BaseModel):
    """Quiz creation schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    content_id: str
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=480)
    max_attempts: int = Field(1, ge=1, le=10)
    passing_score: float = Field(70.0, ge=0.0, le=100.0)
    is_randomized: bool = False
    questions: List[QuestionCreate] = Field(..., min_items=1)


class QuizUpdate(BaseModel):
    """Quiz update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=480)
    max_attempts: Optional[int] = Field(None, ge=1, le=10)
    passing_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    is_randomized: Optional[bool] = None


class QuizResponse(BaseModel):
    """Quiz response schema"""
    quiz_id: str
    title: str
    description: Optional[str]
    content_id: str
    time_limit_minutes: Optional[int]
    max_attempts: int
    passing_score: float
    is_randomized: bool
    is_published: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    questions: List[QuestionResponse] = []


# Quiz Answer Schemas
class QuizAnswerSubmit(BaseModel):
    """Quiz answer submission schema"""
    question_id: str
    selected_choices: Optional[List[str]] = None  # For multiple choice
    text_answer: Optional[str] = Field(None, max_length=2000)  # For short answer


class QuizAttemptSubmit(BaseModel):
    """Quiz attempt submission schema"""
    answers: List[QuizAnswerSubmit]


class QuizAnswerResponse(BaseModel):
    """Quiz answer response schema"""
    answer_id: str
    question_id: str
    selected_choices: Optional[List[str]]
    text_answer: Optional[str]
    is_correct: Optional[bool]
    points_earned: float
    answered_at: datetime


class QuizAttemptResponse(BaseModel):
    """Quiz attempt response schema"""
    attempt_id: str
    quiz_id: str
    user_id: str
    attempt_number: int
    started_at: datetime
    completed_at: Optional[datetime]
    time_spent_minutes: int
    score: Optional[float]
    max_score: float
    is_passed: bool
    status: AttemptStatus
    answers: List[QuizAnswerResponse] = []


# Assessment Schemas
class AssessmentCreate(BaseModel):
    """Assessment creation schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    assessment_type: AssessmentType
    content_id: Optional[str] = None
    due_date: Optional[datetime] = None
    total_points: float = Field(..., ge=0.1)
    passing_score: float = Field(70.0, ge=0.0, le=100.0)


class AssessmentUpdate(BaseModel):
    """Assessment update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
    total_points: Optional[float] = Field(None, ge=0.1)
    passing_score: Optional[float] = Field(None, ge=0.0, le=100.0)


class AssessmentResponse(BaseModel):
    """Assessment response schema"""
    assessment_id: str
    title: str
    description: Optional[str]
    assessment_type: AssessmentType
    content_id: Optional[str]
    due_date: Optional[datetime]
    total_points: float
    passing_score: float
    is_published: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


# Assessment Submission Schemas
class AssessmentSubmissionCreate(BaseModel):
    """Assessment submission creation schema"""
    submission_data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = Field(None, max_length=500)


class AssessmentSubmissionGrade(BaseModel):
    """Assessment submission grading schema"""
    score: float = Field(..., ge=0.0)
    feedback: Optional[str] = Field(None, max_length=2000)


class AssessmentSubmissionResponse(BaseModel):
    """Assessment submission response schema"""
    submission_id: str
    assessment_id: str
    user_id: str
    submission_data: Optional[Dict[str, Any]]
    file_path: Optional[str]
    score: Optional[float]
    feedback: Optional[str]
    graded_by: Optional[str]
    submitted_at: datetime
    graded_at: Optional[datetime]
    status: SubmissionStatus


# List Response Schemas
class QuizListResponse(BaseModel):
    """Quiz list response with pagination"""
    quizzes: List[QuizResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class AssessmentListResponse(BaseModel):
    """Assessment list response with pagination"""
    assessments: List[AssessmentResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class QuizAttemptListResponse(BaseModel):
    """Quiz attempt list response with pagination"""
    attempts: List[QuizAttemptResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class AssessmentSubmissionListResponse(BaseModel):
    """Assessment submission list response with pagination"""
    submissions: List[AssessmentSubmissionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# Statistics Schemas
class QuizStatistics(BaseModel):
    """Quiz statistics schema"""
    quiz_id: str
    quiz_title: str
    total_attempts: int
    completed_attempts: int
    average_score: float
    pass_rate: float
    average_time_minutes: int


class UserQuizStatistics(BaseModel):
    """User quiz statistics schema"""
    user_id: str
    total_quizzes_taken: int
    total_quizzes_passed: int
    average_score: float
    total_time_spent_minutes: int 