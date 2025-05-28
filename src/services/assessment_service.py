"""
Assessment and quiz service
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.models.assessment import (
    Quiz,
    Question,
    QuestionChoice,
    QuizAttempt,
    QuizAnswer,
    Assessment,
    AssessmentSubmission,
)
from src.schemas.assessment import (
    QuizCreate,
    QuizUpdate,
    QuestionCreate,
    QuestionChoiceCreate,
    QuizAttemptSubmit,
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentSubmissionCreate,
    AssessmentSubmissionGrade,
)


class AssessmentService:
    """Service for assessment and quiz management"""

    def __init__(self, db: Session):
        self.db = db

    # Quiz Management
    def create_quiz(self, quiz_data: QuizCreate, created_by: str) -> Quiz:
        """Create a new quiz with questions"""
        quiz = Quiz(
            quiz_id=str(uuid.uuid4()),
            title=quiz_data.title,
            description=quiz_data.description,
            content_id=quiz_data.content_id,
            time_limit_minutes=quiz_data.time_limit_minutes,
            max_attempts=quiz_data.max_attempts,
            passing_score=quiz_data.passing_score,
            is_randomized=quiz_data.is_randomized,
            created_by=created_by,
        )

        self.db.add(quiz)
        self.db.flush()  # Get the quiz_id

        # Add questions
        for question_data in quiz_data.questions:
            question = Question(
                question_id=str(uuid.uuid4()),
                quiz_id=quiz.quiz_id,
                question_text=question_data.question_text,
                question_type=question_data.question_type.value,
                points=question_data.points,
                order_index=question_data.order_index,
                explanation=question_data.explanation,
                is_required=question_data.is_required,
            )

            self.db.add(question)
            self.db.flush()  # Get the question_id

            # Add choices for multiple choice questions
            for choice_data in question_data.choices:
                choice = QuestionChoice(
                    choice_id=str(uuid.uuid4()),
                    question_id=question.question_id,
                    choice_text=choice_data.choice_text,
                    is_correct=choice_data.is_correct,
                    order_index=choice_data.order_index,
                )
                self.db.add(choice)

        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """Get quiz by ID with questions and choices"""
        return (
            self.db.query(Quiz)
            .filter(Quiz.quiz_id == quiz_id)
            .first()
        )

    def get_quizzes(
        self, skip: int = 0, limit: int = 100, content_id: str = None
    ) -> tuple[List[Quiz], int]:
        """Get quizzes with pagination and optional content filter"""
        query = self.db.query(Quiz)

        if content_id:
            query = query.filter(Quiz.content_id == content_id)

        total = query.count()
        quizzes = query.offset(skip).limit(limit).all()

        return quizzes, total

    def update_quiz(self, quiz_id: str, quiz_data: QuizUpdate) -> Optional[Quiz]:
        """Update quiz"""
        quiz = self.db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
        if not quiz:
            return None

        update_data = quiz_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(quiz, field, value)

        quiz.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def delete_quiz(self, quiz_id: str) -> bool:
        """Delete quiz and related data"""
        quiz = self.db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
        if not quiz:
            return False

        # Delete related data (cascade should handle this, but being explicit)
        self.db.query(QuizAnswer).filter(
            QuizAnswer.attempt_id.in_(
                self.db.query(QuizAttempt.attempt_id).filter(
                    QuizAttempt.quiz_id == quiz_id
                )
            )
        ).delete(synchronize_session=False)

        self.db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz_id
        ).delete()

        self.db.query(QuestionChoice).filter(
            QuestionChoice.question_id.in_(
                self.db.query(Question.question_id).filter(
                    Question.quiz_id == quiz_id
                )
            )
        ).delete(synchronize_session=False)

        self.db.query(Question).filter(Question.quiz_id == quiz_id).delete()
        self.db.delete(quiz)
        self.db.commit()
        return True

    def publish_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """Publish quiz"""
        quiz = self.db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
        if not quiz:
            return None

        quiz.is_published = True
        quiz.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    # Quiz Attempt Management
    def start_quiz_attempt(self, quiz_id: str, user_id: str) -> Optional[QuizAttempt]:
        """Start a new quiz attempt"""
        quiz = self.db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
        if not quiz or not quiz.is_published:
            return None

        # Check attempt limit
        attempt_count = (
            self.db.query(QuizAttempt)
            .filter(
                and_(
                    QuizAttempt.quiz_id == quiz_id,
                    QuizAttempt.user_id == user_id,
                )
            )
            .count()
        )

        if attempt_count >= quiz.max_attempts:
            return None

        # Calculate total possible points
        max_score = (
            self.db.query(func.sum(Question.points))
            .filter(Question.quiz_id == quiz_id)
            .scalar() or 0
        )

        attempt = QuizAttempt(
            attempt_id=str(uuid.uuid4()),
            quiz_id=quiz_id,
            user_id=user_id,
            attempt_number=attempt_count + 1,
            max_score=max_score,
        )

        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def submit_quiz_attempt(
        self, attempt_id: str, submission: QuizAttemptSubmit
    ) -> Optional[QuizAttempt]:
        """Submit quiz attempt with answers"""
        attempt = (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.attempt_id == attempt_id)
            .first()
        )
        if not attempt or attempt.status != "in_progress":
            return None

        total_points = 0.0

        # Process each answer
        for answer_data in submission.answers:
            question = (
                self.db.query(Question)
                .filter(Question.question_id == answer_data.question_id)
                .first()
            )
            if not question:
                continue

            # Calculate points based on question type
            points_earned = 0.0
            is_correct = False

            if question.question_type == "multiple_choice":
                if answer_data.selected_choices:
                    correct_choices = (
                        self.db.query(QuestionChoice.choice_id)
                        .filter(
                            and_(
                                QuestionChoice.question_id == question.question_id,
                                QuestionChoice.is_correct == True,
                            )
                        )
                        .all()
                    )
                    correct_choice_ids = {choice.choice_id for choice in correct_choices}
                    selected_choice_ids = set(answer_data.selected_choices)

                    if correct_choice_ids == selected_choice_ids:
                        points_earned = question.points
                        is_correct = True

            elif question.question_type == "true_false":
                if answer_data.selected_choices and len(answer_data.selected_choices) == 1:
                    selected_choice = (
                        self.db.query(QuestionChoice)
                        .filter(
                            QuestionChoice.choice_id == answer_data.selected_choices[0]
                        )
                        .first()
                    )
                    if selected_choice and selected_choice.is_correct:
                        points_earned = question.points
                        is_correct = True

            # For short answer, manual grading required
            elif question.question_type == "short_answer":
                # Auto-grading not implemented, requires manual review
                pass

            # Save answer
            quiz_answer = QuizAnswer(
                answer_id=str(uuid.uuid4()),
                attempt_id=attempt_id,
                question_id=answer_data.question_id,
                selected_choices=answer_data.selected_choices,
                text_answer=answer_data.text_answer,
                is_correct=is_correct,
                points_earned=points_earned,
            )
            self.db.add(quiz_answer)
            total_points += points_earned

        # Update attempt
        attempt.completed_at = datetime.utcnow()
        attempt.score = (total_points / attempt.max_score * 100) if attempt.max_score > 0 else 0
        attempt.is_passed = attempt.score >= attempt.quiz.passing_score
        attempt.status = "completed"

        # Calculate time spent
        time_diff = attempt.completed_at - attempt.started_at
        attempt.time_spent_minutes = int(time_diff.total_seconds() / 60)

        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def get_quiz_attempts(
        self, quiz_id: str = None, user_id: str = None, skip: int = 0, limit: int = 100
    ) -> tuple[List[QuizAttempt], int]:
        """Get quiz attempts with optional filters"""
        query = self.db.query(QuizAttempt)

        if quiz_id:
            query = query.filter(QuizAttempt.quiz_id == quiz_id)
        if user_id:
            query = query.filter(QuizAttempt.user_id == user_id)

        total = query.count()
        attempts = query.offset(skip).limit(limit).all()

        return attempts, total

    # Assessment Management
    def create_assessment(
        self, assessment_data: AssessmentCreate, created_by: str
    ) -> Assessment:
        """Create a new assessment"""
        assessment = Assessment(
            assessment_id=str(uuid.uuid4()),
            title=assessment_data.title,
            description=assessment_data.description,
            assessment_type=assessment_data.assessment_type.value,
            content_id=assessment_data.content_id,
            due_date=assessment_data.due_date,
            total_points=assessment_data.total_points,
            passing_score=assessment_data.passing_score,
            created_by=created_by,
        )

        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def get_assessment(self, assessment_id: str) -> Optional[Assessment]:
        """Get assessment by ID"""
        return (
            self.db.query(Assessment)
            .filter(Assessment.assessment_id == assessment_id)
            .first()
        )

    def get_assessments(
        self, skip: int = 0, limit: int = 100, content_id: str = None
    ) -> tuple[List[Assessment], int]:
        """Get assessments with pagination and optional content filter"""
        query = self.db.query(Assessment)

        if content_id:
            query = query.filter(Assessment.content_id == content_id)

        total = query.count()
        assessments = query.offset(skip).limit(limit).all()

        return assessments, total

    def update_assessment(
        self, assessment_id: str, assessment_data: AssessmentUpdate
    ) -> Optional[Assessment]:
        """Update assessment"""
        assessment = (
            self.db.query(Assessment)
            .filter(Assessment.assessment_id == assessment_id)
            .first()
        )
        if not assessment:
            return None

        update_data = assessment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assessment, field, value)

        assessment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def delete_assessment(self, assessment_id: str) -> bool:
        """Delete assessment and related submissions"""
        assessment = (
            self.db.query(Assessment)
            .filter(Assessment.assessment_id == assessment_id)
            .first()
        )
        if not assessment:
            return False

        # Delete related submissions
        self.db.query(AssessmentSubmission).filter(
            AssessmentSubmission.assessment_id == assessment_id
        ).delete()

        self.db.delete(assessment)
        self.db.commit()
        return True

    def publish_assessment(self, assessment_id: str) -> Optional[Assessment]:
        """Publish assessment"""
        assessment = (
            self.db.query(Assessment)
            .filter(Assessment.assessment_id == assessment_id)
            .first()
        )
        if not assessment:
            return None

        assessment.is_published = True
        assessment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    # Assessment Submission Management
    def submit_assessment(
        self, assessment_id: str, user_id: str, submission_data: AssessmentSubmissionCreate
    ) -> Optional[AssessmentSubmission]:
        """Submit assessment"""
        assessment = (
            self.db.query(Assessment)
            .filter(Assessment.assessment_id == assessment_id)
            .first()
        )
        if not assessment or not assessment.is_published:
            return None

        submission = AssessmentSubmission(
            submission_id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            user_id=user_id,
            submission_data=submission_data.submission_data,
            file_path=submission_data.file_path,
        )

        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def grade_submission(
        self, submission_id: str, grade_data: AssessmentSubmissionGrade, graded_by: str
    ) -> Optional[AssessmentSubmission]:
        """Grade assessment submission"""
        submission = (
            self.db.query(AssessmentSubmission)
            .filter(AssessmentSubmission.submission_id == submission_id)
            .first()
        )
        if not submission:
            return None

        submission.score = grade_data.score
        submission.feedback = grade_data.feedback
        submission.graded_by = graded_by
        submission.graded_at = datetime.utcnow()
        submission.status = "graded"

        self.db.commit()
        self.db.refresh(submission)
        return submission

    def get_assessment_submissions(
        self, assessment_id: str = None, user_id: str = None, skip: int = 0, limit: int = 100
    ) -> tuple[List[AssessmentSubmission], int]:
        """Get assessment submissions with optional filters"""
        query = self.db.query(AssessmentSubmission)

        if assessment_id:
            query = query.filter(AssessmentSubmission.assessment_id == assessment_id)
        if user_id:
            query = query.filter(AssessmentSubmission.user_id == user_id)

        total = query.count()
        submissions = query.offset(skip).limit(limit).all()

        return submissions, total

    # Statistics
    def get_quiz_statistics(self, quiz_id: str) -> Dict[str, Any]:
        """Get quiz statistics"""
        quiz = self.db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
        if not quiz:
            return None

        attempts = (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.quiz_id == quiz_id)
            .all()
        )

        completed_attempts = [a for a in attempts if a.status == "completed"]
        total_attempts = len(attempts)
        completed_count = len(completed_attempts)

        if completed_count == 0:
            return {
                "quiz_id": quiz_id,
                "quiz_title": quiz.title,
                "total_attempts": total_attempts,
                "completed_attempts": 0,
                "average_score": 0.0,
                "pass_rate": 0.0,
                "average_time_minutes": 0,
            }

        average_score = sum(a.score for a in completed_attempts) / completed_count
        passed_count = sum(1 for a in completed_attempts if a.is_passed)
        pass_rate = (passed_count / completed_count) * 100
        average_time = sum(a.time_spent_minutes for a in completed_attempts) / completed_count

        return {
            "quiz_id": quiz_id,
            "quiz_title": quiz.title,
            "total_attempts": total_attempts,
            "completed_attempts": completed_count,
            "average_score": round(average_score, 2),
            "pass_rate": round(pass_rate, 2),
            "average_time_minutes": round(average_time),
        }

    def get_user_quiz_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user quiz statistics"""
        attempts = (
            self.db.query(QuizAttempt)
            .filter(
                and_(
                    QuizAttempt.user_id == user_id,
                    QuizAttempt.status == "completed",
                )
            )
            .all()
        )

        if not attempts:
            return {
                "user_id": user_id,
                "total_quizzes_taken": 0,
                "total_quizzes_passed": 0,
                "average_score": 0.0,
                "total_time_spent_minutes": 0,
            }

        total_quizzes = len(attempts)
        passed_quizzes = sum(1 for a in attempts if a.is_passed)
        average_score = sum(a.score for a in attempts) / total_quizzes
        total_time = sum(a.time_spent_minutes for a in attempts)

        return {
            "user_id": user_id,
            "total_quizzes_taken": total_quizzes,
            "total_quizzes_passed": passed_quizzes,
            "average_score": round(average_score, 2),
            "total_time_spent_minutes": total_time,
        } 