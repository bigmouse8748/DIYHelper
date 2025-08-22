"""
User Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


class UserTypeEnum(str, Enum):
    """User type enumeration"""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User registration schema"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    user_type: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        orm_mode = True
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Optional[UserResponse] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserUpdate(BaseModel):
    """User update schema for admin"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    user_type: Optional[UserTypeEnum] = None
    is_active: Optional[bool] = None
    email_verified: Optional[bool] = None
    phone: Optional[str] = None
    location: Optional[str] = None


class UserListResponse(BaseModel):
    """User list response for admin"""
    users: list[UserResponse]
    total: int
    page: int
    size: int
    pages: int


class UserCreateAdmin(UserBase):
    """Admin user creation schema"""
    password: str = Field(..., min_length=8, max_length=100)
    user_type: UserTypeEnum = UserTypeEnum.FREE
    is_active: bool = True
    email_verified: bool = False
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v