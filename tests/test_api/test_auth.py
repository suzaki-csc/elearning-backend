"""
Tests for authentication API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app
from src.schemas.auth import UserRegistration


class TestAuthAPI:
    """Test authentication API endpoints"""

    def test_register_user(self, client: TestClient):
        """Test user registration"""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "display_name": "Test User",
            "department": "Engineering",
            "position": "Developer"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["display_name"] == user_data["display_name"]
        assert "user_id" in data
        assert "password" not in data  # Password should not be returned

    def test_register_duplicate_email(self, client: TestClient):
        """Test registration with duplicate email"""
        user_data = {
            "email": "duplicate@example.com",
            "password": "testpassword123",
            "display_name": "Test User"
        }
        
        # First registration should succeed
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Second registration with same email should fail
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]

    def test_login_success(self, client: TestClient):
        """Test successful login"""
        # First register a user
        user_data = {
            "email": "login@example.com",
            "password": "testpassword123",
            "display_name": "Login User"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Then login
        login_data = {
            "email": "login@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_get_current_user(self, client: TestClient):
        """Test getting current user info with valid token"""
        # Register and login
        user_data = {
            "email": "current@example.com",
            "password": "testpassword123",
            "display_name": "Current User"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "email": "current@example.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Get current user info
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["display_name"] == user_data["display_name"]

    def test_verify_token(self, client: TestClient):
        """Test token verification"""
        # Register and login
        user_data = {
            "email": "verify@example.com",
            "password": "testpassword123",
            "display_name": "Verify User"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "email": "verify@example.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Verify token
        response = client.post(
            "/api/v1/auth/verify-token",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert "user_id" in data
        assert data["email"] == user_data["email"]

    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access"""
        response = client.get("/api/v1/auth/me")
        # FastAPI returns 403 when no credentials are provided with HTTPBearer
        assert response.status_code == 403

    def test_invalid_token(self, client: TestClient):
        """Test access with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_logout(self, client: TestClient):
        """Test user logout"""
        # Register and login
        user_data = {
            "email": "logout@example.com",
            "password": "testpassword123",
            "display_name": "Logout User"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "email": "logout@example.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Logout
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"] 