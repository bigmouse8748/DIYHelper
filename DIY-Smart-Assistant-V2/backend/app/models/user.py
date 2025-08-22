"""
User Model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from .base import Base, TimestampMixin


class UserType(enum.Enum):
    """User type enumeration"""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    avatar_url = Column(String(500))
    
    user_type = Column(String(10), default="free", nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verify_token = Column(String(64))
    
    password_reset_token = Column(String(64))
    password_reset_expires = Column(DateTime(timezone=True))
    
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    
    last_login = Column(DateTime(timezone=True))
    phone = Column(String(20))
    location = Column(String(100))
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    def get_permissions(self):
        """Get user permissions based on user type"""
        permissions_map = {
            "free": {
                "tool_identification": {"daily_limit": 5},
                "project_analysis": {"daily_limit": 2},
                "product_view": True,
                "history_days": 7
            },
            "pro": {
                "tool_identification": {"daily_limit": 20},
                "project_analysis": {"daily_limit": 10},
                "product_view": True,
                "history_days": 30
            },
            "premium": {
                "tool_identification": {"daily_limit": -1},  # Unlimited
                "project_analysis": {"daily_limit": -1},
                "product_view": True,
                "history_days": -1
            },
            "admin": {
                "all_permissions": True,
                "user_management": True,
                "product_management": True,
                "system_analytics": True
            }
        }
        return permissions_map.get(self.user_type, permissions_map["free"])


class UserSession(Base, TimestampMixin):
    """User session model for tracking login sessions"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Relationship
    user = relationship("User", back_populates="sessions")


class RefreshToken(Base, TimestampMixin):
    """Refresh token management"""
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(36), unique=True, index=True, nullable=False)  # JWT ID
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True))
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="refresh_tokens")