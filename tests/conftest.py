"""
Pytest configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.config.database import get_db, Base


# Create test database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create test database session"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client"""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "display_name": "Test User",
        "department": "Engineering",
        "position": "Developer",
    }


@pytest.fixture
def admin_user_data():
    """Admin user data"""
    return {
        "email": "admin@example.com",
        "password": "adminpassword123",
        "display_name": "Admin User",
        "department": "Management",
        "position": "Administrator",
    }


@pytest.fixture
def user_token(client: TestClient, test_user_data):
    """Create a test user and return access token"""
    # Register user
    client.post("/api/v1/auth/register", json=test_user_data)

    # Login and get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )

    return login_response.json()["access_token"]


@pytest.fixture
def admin_token(client: TestClient, admin_user_data):
    """Create an admin user and return access token"""
    # Register admin user
    client.post("/api/v1/auth/register", json=admin_user_data)

    # Login and get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user_data["email"],
            "password": admin_user_data["password"],
        },
    )

    return login_response.json()["access_token"]
