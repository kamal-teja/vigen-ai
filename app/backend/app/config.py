from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # DynamoDB Tables
    USERS_TABLE: str
    ADVERTISEMENTS_TABLE: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours (increased from 30 minutes)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days

    # AWS S3
    # Make credentials optional to support IAM roles (App Runner, ECS, EC2)
    # For local dev, set these in .env; for production, use IAM roles
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str
    S3_BUCKET_NAME: str

    # Crew Endpoint
    CREW_ENDPOINT_URL: Optional[str] = "http://localhost:8001"  # Default placeholder

    # Application
    DEBUG: bool = False
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        case_sensitive = True


settings = Settings()
