"""
Application settings configuration
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "E-Learning System"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Password Requirements
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_UPPERCASE: bool = False
    REQUIRE_LOWERCASE: bool = False
    REQUIRE_NUMBERS: bool = False
    REQUIRE_SPECIAL_CHARS: bool = False

    # Rate Limiting
    LOGIN_RATE_LIMIT: int = 5  # Max login attempts per minute
    REGISTRATION_RATE_LIMIT: int = 3  # Max registrations per hour

    # Database
    DATABASE_URL: str = "mysql+pymysql://elearning:password@localhost:3306/elearning_db"
    TEST_DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # AWS Settings (for future use)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-northeast-1"
    S3_BUCKET_NAME: Optional[str] = None

    # Google Workspace (for future use)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # Email Settings (for password reset, etc.)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
