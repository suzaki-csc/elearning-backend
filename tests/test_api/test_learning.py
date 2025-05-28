"""
Tests for learning progress API endpoints
"""

from fastapi.testclient import TestClient


class TestLearningAPI:
    """Test learning progress API endpoints"""

    def test_update_progress(self, client: TestClient, user_token: str):
        """Test updating user progress"""
        # First create a content
        content_data = {
            "title": "Test Learning Content",
            "description": "Test content for learning",
            "content_type": "video",
            "duration_minutes": 30,
        }

        content_response = client.post(
            "/api/v1/contents/",
            json=content_data,
            headers={"Authorization": f"Bearer {user_token}"},
        )
        content_id = content_response.json()["content_id"]

        # Update progress
        progress_data = {"progress_percentage": 50.0, "time_spent_minutes": 15}

        response = client.post(
            f"/api/v1/learning/progress/{content_id}",
            json=progress_data,
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["progress_percentage"] == 50.0
        assert data["is_completed"] is False

    def test_get_content_progress(self, client: TestClient, user_token: str):
        """Test getting user progress for content"""
        # Create content and update progress first
        content_data = {
            "title": "Test Content Progress",
            "description": "Test content",
            "content_type": "document",
        }

        content_response = client.post(
            "/api/v1/contents/",
            json=content_data,
            headers={"Authorization": f"Bearer {user_token}"},
        )
        content_id = content_response.json()["content_id"]

        # Update progress
        progress_data = {"progress_percentage": 100.0, "time_spent_minutes": 30}
        client.post(
            f"/api/v1/learning/progress/{content_id}",
            json=progress_data,
            headers={"Authorization": f"Bearer {user_token}"},
        )

        # Get progress
        response = client.get(
            f"/api/v1/learning/progress/{content_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["progress_percentage"] == 100.0
        assert data["is_completed"] is True

    def test_get_user_progress_summary(self, client: TestClient, user_token: str):
        """Test getting user progress summary"""
        response = client.get(
            "/api/v1/learning/summary",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_contents" in data
        assert "completed_contents" in data
        assert "completion_rate" in data

    def test_create_assignment_admin_only(self, client: TestClient, admin_token: str):
        """Test creating assignment (admin only)"""
        # Create content first
        content_data = {
            "title": "Assignment Content",
            "description": "Content for assignment",
            "content_type": "quiz",
        }

        content_response = client.post(
            "/api/v1/contents/",
            json=content_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        content_id = content_response.json()["content_id"]

        # Create user for assignment
        user_data = {
            "email": "assignee@example.com",
            "password": "password123",
            "display_name": "Assignee User",
        }
        user_response = client.post("/api/v1/auth/register", json=user_data)
        user_id = user_response.json()["user_id"]

        # Create assignment
        assignment_data = {
            "user_id": user_id,
            "content_id": content_id,
            "is_mandatory": True,
            "notes": "Please complete this assignment",
        }

        response = client.post(
            "/api/v1/learning/assignments",
            json=assignment_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["content_id"] == content_id
        assert data["is_mandatory"] is True

    def test_get_user_assignments(self, client: TestClient, user_token: str):
        """Test getting user assignments"""
        response = client.get(
            "/api/v1/learning/assignments",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "assignments" in data
        assert "total" in data
        assert "page" in data

    def test_create_learning_path(self, client: TestClient, admin_token: str):
        """Test creating learning path (admin only)"""
        # Create multiple contents
        content_ids = []
        for i in range(3):
            content_data = {
                "title": f"Path Content {i+1}",
                "description": f"Content {i+1} for learning path",
                "content_type": "video",
            }

            content_response = client.post(
                "/api/v1/contents/",
                json=content_data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            content_ids.append(content_response.json()["content_id"])

        # Create learning path
        path_data = {
            "title": "Complete Learning Path",
            "description": "A comprehensive learning path",
            "content_ids": content_ids,
        }

        response = client.post(
            "/api/v1/learning/paths",
            json=path_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Complete Learning Path"
        assert len(data["contents"]) == 3

    def test_get_learning_paths(self, client: TestClient, user_token: str):
        """Test getting learning paths"""
        response = client.get(
            "/api/v1/learning/paths",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "paths" in data
        assert "total" in data

    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to learning endpoints"""
        response = client.get("/api/v1/learning/summary")
        assert response.status_code == 403
