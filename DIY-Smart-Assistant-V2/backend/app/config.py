"""
Application Configuration
Manages all configuration settings using Pydantic Settings
"""

from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings
import secrets
import os


class Settings(BaseSettings):
    """Application settings configuration"""
    
    # Application
    app_name: str = "DIY Smart Assistant"
    app_version: str = "2.0.0"
    debug: bool = False  # Default to False for production
    secret_key: str = secrets.token_urlsafe(32)
    
    # Database
    database_url: str = "sqlite:///./diy_assistant.db"
    
    # Database connection components (for production)
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_name: Optional[str] = None
    
    # Authentication
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-vision-preview"
    
    # File Upload
    max_file_size_mb: int = 10
    allowed_file_types: str = "jpg,jpeg,png,webp"
    upload_path: str = "uploads/"
    
    # CORS
    allowed_origins: str = "*"
    
    # Email (Optional)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = ""
    base_url: str = "http://localhost:8000"
    
    # Redis (Optional)
    redis_url: str = "redis://localhost:6379"
    
    # Sentry (Optional)  
    sentry_dsn: str = ""
    
    @validator("database_url")
    def build_database_url(cls, v, values):
        """Build database URL from individual components if available"""
        # If we have individual database components, build PostgreSQL URL
        db_host = values.get('db_host') or os.getenv('DB_HOST')
        db_port = values.get('db_port') or os.getenv('DB_PORT')
        db_user = values.get('db_user') or os.getenv('DB_USER')
        db_password = values.get('db_password') or os.getenv('DB_PASSWORD')
        db_name = values.get('db_name') or os.getenv('DB_NAME')
        
        if all([db_host, db_user, db_password, db_name]):
            port = db_port or 5432
            return f"postgresql://{db_user}:{db_password}@{db_host}:{port}/{db_name}"
        
        # Otherwise use the provided database_url or DATABASE_URL env var
        return os.getenv('DATABASE_URL', v)
    
    @validator("allowed_origins")
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins"""
        if v.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    
    @validator("allowed_file_types")
    def parse_file_types(cls, v: str) -> List[str]:
        """Parse comma-separated file types"""
        return [ft.strip().lower() for ft in v.split(",") if ft.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings