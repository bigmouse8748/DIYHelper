"""
Application Configuration
Manages all configuration settings using Pydantic Settings
"""

from typing import List
from pydantic import validator
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    """Application settings configuration"""
    
    # Application
    app_name: str = "DIY Smart Assistant"
    app_version: str = "2.0.0"
    debug: bool = True
    secret_key: str = secrets.token_urlsafe(32)
    
    # Database
    database_url: str = "sqlite:///./diy_assistant.db"
    
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