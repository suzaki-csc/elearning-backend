"""
Tests for content API endpoints
"""

from fastapi.testclient import TestClient

from src.schemas.content import ContentType


class TestContentAPI:
    """Test content API endpoints"""

    def test_create_category(self, client: TestClient, admin_token: str):
        """Test category creation"""
        category_data = {"name": "Programming", "description": "Programming courses"}

        response = client.post(
            "/api/v1/contents/categories",
            json=category_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["description"] == category_data["description"]
        assert "category_id" in data

    def test_get_categories(self, client: TestClient, user_token: str):
        """Test getting categories"""
        response = client.get(
            "/api/v1/contents/categories",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "total" in data
        assert "page" in data

    def test_create_content(self, client: TestClient, admin_token: str):
        """Test content creation"""
        content_data = {
            "title": "Python Basics",
            "description": "Learn Python programming basics",
            "content_type": ContentType.VIDEO.value,
            "duration_minutes": 60,
        }

        response = client.post(
            "/api/v1/contents/",
            json=content_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == content_data["title"]
        assert data["content_type"] == content_data["content_type"]
        assert "content_id" in data

    def test_get_contents(self, client: TestClient, user_token: str):
        """Test getting contents"""
        response = client.get(
            "/api/v1/contents/", headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "contents" in data
        assert "total" in data
        assert "page" in data

    def test_search_contents(self, client: TestClient, user_token: str):
        """Test content search"""
        response = client.get(
            "/api/v1/contents/?search=Python",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "contents" in data

    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to admin endpoints"""
        # Try to create category without authentication
        response = client.post(
            "/api/v1/contents/categories",
            json={"name": "Test Category", "description": "Test Description"},
        )
        # FastAPI returns 403 when no credentials are provided with HTTPBearer
        assert response.status_code == 403
