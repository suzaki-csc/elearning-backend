"""
Assessment and quiz models
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from src.models.base import Base


class Quiz(Base):
    """Quiz model"""

    __tablename__ = "quizzes"

    quiz_id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content_id = Column(String(36), ForeignKey("contents.content_id"), nullable=False)
    time_limit_minutes = Column(Integer, nullable=True)  # Time limit in minutes
    max_attempts = Column(Integer, default=1, nullable=False)
    passing_score = Column(Float, default=70.0, nullable=False)  # Percentage
    is_randomized = Column(Boolean, default=False, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    content = relationship("Content")
    creator = relationship("User")
    questions = relationship("Question", back_populates="quiz")


class Question(Base):
    """Question model"""

    __tablename__ = "questions"

    question_id = Column(String(36), primary_key=True)
    quiz_id = Column(String(36), ForeignKey("quizzes.quiz_id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # multiple_choice, true_false, short_answer
    points = Column(Float, default=1.0, nullable=False)
    order_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)  # Explanation for correct answer
    is_required = Column(Boolean, default=True, nullable=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    choices = relationship("QuestionChoice", back_populates="question")


class QuestionChoice(Base):
    """Question choice model for multiple choice questions"""

    __tablename__ = "question_choices"

    choice_id = Column(String(36), primary_key=True)
    question_id = Column(String(36), ForeignKey("questions.question_id"), nullable=False)
    choice_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    order_index = Column(Integer, nullable=False)

    # Relationships
    question = relationship("Question", back_populates="choices")


class QuizAttempt(Base):
    """Quiz attempt model"""

    __tablename__ = "quiz_attempts"

    attempt_id = Column(String(36), primary_key=True)
    quiz_id = Column(String(36), ForeignKey("quizzes.quiz_id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    time_spent_minutes = Column(Integer, default=0, nullable=False)
    score = Column(Float, nullable=True)  # Percentage score
    max_score = Column(Float, nullable=False)  # Total possible points
    is_passed = Column(Boolean, default=False, nullable=False)
    status = Column(String(20), default="in_progress", nullable=False)  # in_progress, completed, abandoned

    # Relationships
    quiz = relationship("Quiz")
    user = relationship("User")
    answers = relationship("QuizAnswer", back_populates="attempt")


class QuizAnswer(Base):
    """Quiz answer model"""

    __tablename__ = "quiz_answers"

    answer_id = Column(String(36), primary_key=True)
    attempt_id = Column(String(36), ForeignKey("quiz_attempts.attempt_id"), nullable=False)
    question_id = Column(String(36), ForeignKey("questions.question_id"), nullable=False)
    selected_choices = Column(JSON, nullable=True)  # For multiple choice questions
    text_answer = Column(Text, nullable=True)  # For short answer questions
    is_correct = Column(Boolean, nullable=True)
    points_earned = Column(Float, default=0.0, nullable=False)
    answered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("Question")


class Assessment(Base):
    """Assessment model for comprehensive evaluations"""

    __tablename__ = "assessments"

    assessment_id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    assessment_type = Column(String(50), nullable=False)  # quiz, exam, assignment, project
    content_id = Column(String(36), ForeignKey("contents.content_id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    total_points = Column(Float, nullable=False)
    passing_score = Column(Float, default=70.0, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    content = relationship("Content")
    creator = relationship("User")
    submissions = relationship("AssessmentSubmission", back_populates="assessment")


class AssessmentSubmission(Base):
    """Assessment submission model"""

    __tablename__ = "assessment_submissions"

    submission_id = Column(String(36), primary_key=True)
    assessment_id = Column(String(36), ForeignKey("assessments.assessment_id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    submission_data = Column(JSON, nullable=True)  # Flexible data storage
    file_path = Column(String(500), nullable=True)  # For file submissions
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    graded_by = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    graded_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="submitted", nullable=False)  # submitted, graded, returned

    # Relationships
    assessment = relationship("Assessment", back_populates="submissions")
    user = relationship("User", foreign_keys=[user_id])
    grader = relationship("User", foreign_keys=[graded_by]) 