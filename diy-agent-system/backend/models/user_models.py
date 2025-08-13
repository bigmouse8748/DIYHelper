"""
User and membership related database models
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class MembershipLevel(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    membership_level = Column(SQLEnum(MembershipLevel), default=MembershipLevel.FREE)
    membership_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    daily_identifications = Column(Integer, default=0)
    last_reset = Column(DateTime, default=datetime.utcnow)
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(password, self.password_hash)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storing"""
        return pwd_context.hash(password)
    
    def get_daily_limit(self) -> int:
        """Get daily identification limit based on membership"""
        limits = {
            MembershipLevel.FREE: 5,
            MembershipLevel.PREMIUM: 50,
            MembershipLevel.PRO: 999999  # Effectively unlimited
        }
        return limits.get(self.membership_level, 5)
    
    def can_identify(self) -> bool:
        """Check if user can perform identification"""
        # Reset daily count if needed
        if self.last_reset.date() < datetime.utcnow().date():
            self.daily_identifications = 0
            self.last_reset = datetime.utcnow()
        
        return self.daily_identifications < self.get_daily_limit()
    
    def has_premium_features(self) -> bool:
        """Check if user has premium features"""
        if self.membership_level in [MembershipLevel.PREMIUM, MembershipLevel.PRO]:
            if self.membership_expiry is None or self.membership_expiry > datetime.utcnow():
                return True
        return False