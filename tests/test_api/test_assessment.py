"""
Tests for assessment and quiz API endpoints
"""

from fastapi.testclient import TestClient


class TestAssessmentAPI:
    """Test assessment and quiz API endpoints"""

    def test_create_quiz(self, client: TestClient, admin_token: str):
        """Test creating a quiz (admin only)"""
        # First create a content
        content_data = {
            "title": "Quiz Content",
            "description": "Content for quiz",
            "content_type": "quiz",
        }

        content_response = client.post(
            "/api/v1/contents/",
            json=content_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        content_id = content_response.json()["content_id"]

        # Create quiz
        quiz_data = {
            "title": "Sample Quiz",
            "description": "A sample quiz for testing",
            "content_id": content_id,
            "time_limit_minutes": 30,
            "max_attempts": 3,
            "passing_score": 70.0,
            "is_randomized": False,
            "questions": [
                {
                    "question_text": "What is 2 + 2?",
                    "question_type": "multiple_choice",
                    "points": 1.0,
                    "order_index": 0,
                    "explanation": "Basic arithmetic",
                    "is_required": True,
                    "choices": [
                        {"choice_text": "3", "is_correct": False, "order_index": 0},
                        {"choice_text": "4", "is_correct": True, "order_index": 1},
                        {"choice_text": "5", "is_correct": False, "order_index": 2},
                    ],
                },
                {
                    "question_text": "Python is a programming language",
                    "question_type": "true_false",
                    "points": 1.0,
                    "order_index": 1,
                    "is_required": True,
                    "choices": [
                        {"choice_text": "True", "is_correct": True, "order_index": 0},
                        {"choice_text": "False", "is_correct": False, "order_index": 1},
                    ],
                },
            ],
        }

        response = client.post(
            "/api/v1/assessment/quizzes",
            json=quiz_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Sample Quiz"
        assert len(data["questions"]) == 2
        assert data["max_attempts"] == 3

    def test_get_quizzes(self, client: TestClient, user_token: str):
        """Test getting quizzes list"""
        response = client.get(
            "/api/v1/assessment/quizzes",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "quizzes" in data
        assert "total" in data

    def test_publish_quiz(self, client: TestClient, admin_token: str):
        """Test publishing a quiz"""
        # Create content and quiz first
        content_data = {
            "title": "Publishable Quiz Content",
            "description": "Content for publishable quiz",
            "content_type": "quiz",
        }

        content_response = client.post(
            "/api/v1/contents/",
            json=content_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        content_id = content_response.json()["content_id"]

        quiz_data = {
            "title": "Publishable Quiz",
            "description": "A quiz to be published",
            "content_id": content_id,
            "questions": [
                {
                    "question_text": "Test question",
                    "question_type": "multiple_choice",
                    "points": 1.0,
                    "order_index": 0,
                    "is_required": True,
                    "choices": [
                        {"choice_text": "A", "is_correct": True, "order_index": 0},
                        {"choice_text": "B", "is_correct": False, "order_index": 1},
                    ],
                }
            ],
        }

        quiz_response = client.post(
            "/api/v1/assessment/quizzes",
            json=quiz_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        quiz_id = quiz_response.json()["quiz_id"]

        # Publish quiz
        response = client.post(
            f"/api/v1/assessment/quizzes/{quiz_id}/publish",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        assert "Quiz published successfully" in response.json()["message"]

    def test_start_quiz_attempt(self, client: TestClient, user_token: str, admin_token: str):
        """Test starting a quiz attempt"""
        # Create and publish a quiz first
        content_data = {
            "title": "Attempt Quiz Content",
            "description": "Content for attempt quiz",
            "content_type": "quiz",
        }

        content_response = client.post(
            "/api/v1/contents/",
            json=content_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        content_id = content_response.json()["content_id"]

        quiz_data = {
            "title": "Attempt Quiz",
            "description": "A quiz for attempt testing",
            "content_id": content_id,
            "questions": [
                {
                    "question_text": "Sample question",
                    "question_type": "multiple_choice",
                    "points": 1.0,
                    "order_index": 0,
                    "is_required": True,
                    "choices": [
                        {"choice_text": "Option A", "is_correct": True, "order_index": 0},
                        {"choice_text": "Option B", "is_correct": False, "order_index": 1},
                    ],
                }
            ],
        }

        quiz_response = client.post(
            "/api/v1/assessment/quizzes",
            json=quiz_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        quiz_id = quiz_response.json()["quiz_id"]

        # Publish quiz
        client.post(
            f"/api/v1/assessment/quizzes/{quiz_id}/publish",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # Start attempt
        response = client.post(
            f"/api/v1/assessment/quizzes/{quiz_id}/attempts",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["quiz_id"] == quiz_id
        assert data["attempt_number"] == 1
        assert data["status"] == "in_progress"

    def test_submit_quiz_attempt(self, client: TestClient, user_token: str, admin_token: str):
        """Test submitting a quiz attempt"""
        # Create and publish a quiz first
        content_data = {
            "title": "Submit Quiz Content",
            "description": "Content for submit quiz",
            "content_type": "quiz",
        }

        content_response = client.post(
            "/api/v1/contents/",
            json=content_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        content_id = content_response.json()["content_id"]

        quiz_data = {
            "title": "Submit Quiz",
            "description": "A quiz for submission testing",
            "content_id": content_id,
            "questions": [
                {
                    "question_text": "What is the capital of Japan?",
                    "question_type": "multiple_choice",
                    "points": 1.0,
                    "order_index": 0,
                    "is_required": True,
                    "choices": [
                        {"choice_text": "Tokyo", "is_correct": True, "order_index": 0},
                        {"choice_text": "Osaka", "is_correct": False, "order_index": 1},
                        {"choice_text": "Kyoto", "is_correct": False, "order_index": 2},
                    ],
                }
            ],
        }

        quiz_response = client.post(
            "/api/v1/assessment/quizzes",
            json=quiz_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        quiz_id = quiz_response.json()["quiz_id"]
        question_id = quiz_response.json()["questions"][0]["question_id"]
        correct_choice_id = quiz_response.json()["questions"][0]["choices"][0]["choice_id"]

        # Publish quiz
        client.post(
            f"/api/v1/assessment/quizzes/{quiz_id}/publish",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # Start attempt
        attempt_response = client.post(
            f"/api/v1/assessment/quizzes/{quiz_id}/attempts",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        attempt_id = attempt_response.json()["attempt_id"]

        # Submit answers
        submission_data = {
            "answers": [
                {
                    "question_id": question_id,
                    "selected_choices": [correct_choice_id],
                }
            ]
        }

        response = client.post(
            f"/api/v1/assessment/attempts/{attempt_id}/submit",
            json=submission_data,
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["score"] == 100.0  # Should be 100% for correct answer
        assert data["is_passed"] is True

    def test_create_assessment(self, client: TestClient, admin_token: str):
        """Test creating an assessment"""
        assessment_data = {
            "title": "Final Project",
            "description": "Complete the final project assignment",
            "assessment_type": "project",
            "total_points": 100.0,
            "passing_score": 80.0,
        }

        response = client.post(
            "/api/v1/assessment/assessments",
            json=assessment_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Final Project"
        assert data["assessment_type"] == "project"
        assert data["total_points"] == 100.0

    def test_get_assessments(self, client: TestClient, user_token: str):
        """Test getting assessments list"""
        response = client.get(
            "/api/v1/assessment/assessments",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "assessments" in data
        assert "total" in data

    def test_submit_assessment(self, client: TestClient, user_token: str, admin_token: str):
        """Test submitting an assessment"""
        # Create and publish assessment first
        assessment_data = {
            "title": "Submission Test Assessment",
            "description": "Assessment for submission testing",
            "assessment_type": "assignment",
            "total_points": 50.0,
            "passing_score": 70.0,
        }

        assessment_response = client.post(
            "/api/v1/assessment/assessments",
            json=assessment_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assessment_id = assessment_response.json()["assessment_id"]

        # Publish assessment
        client.post(
            f"/api/v1/assessment/assessments/{assessment_id}/publish",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # Submit assessment
        submission_data = {
            "submission_data": {"answer": "This is my submission"},
        }

        response = client.post(
            f"/api/v1/assessment/assessments/{assessment_id}/submissions",
            json=submission_data,
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["assessment_id"] == assessment_id
        assert data["status"] == "submitted"

    def test_get_quiz_statistics(self, client: TestClient, admin_token: str):
        """Test getting quiz statistics (admin only)"""
        # Create a quiz first
        content_data = {
            "title": "Stats Quiz Content",
            "description": "Content for stats quiz",
            "content_type": "quiz",
        }

        content_response = client.post(
            "/api/v1/contents/",
            json=content_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        content_id = content_response.json()["content_id"]

        quiz_data = {
            "title": "Statistics Quiz",
            "description": "A quiz for statistics testing",
            "content_id": content_id,
            "questions": [
                {
                    "question_text": "Test question for stats",
                    "question_type": "multiple_choice",
                    "points": 1.0,
                    "order_index": 0,
                    "is_required": True,
                    "choices": [
                        {"choice_text": "A", "is_correct": True, "order_index": 0},
                        {"choice_text": "B", "is_correct": False, "order_index": 1},
                    ],
                }
            ],
        }

        quiz_response = client.post(
            "/api/v1/assessment/quizzes",
            json=quiz_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        quiz_id = quiz_response.json()["quiz_id"]

        # Get statistics
        response = client.get(
            f"/api/v1/assessment/quizzes/{quiz_id}/statistics",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["quiz_id"] == quiz_id
        assert "total_attempts" in data
        assert "average_score" in data

    def test_get_my_quiz_statistics(self, client: TestClient, user_token: str):
        """Test getting current user's quiz statistics"""
        response = client.get(
            "/api/v1/assessment/my-quiz-statistics",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_quizzes_taken" in data
        assert "average_score" in data

    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to assessment endpoints"""
        response = client.get("/api/v1/assessment/quizzes")
        assert response.status_code == 403

        response = client.post("/api/v1/assessment/quizzes", json={})
        assert response.status_code == 403 