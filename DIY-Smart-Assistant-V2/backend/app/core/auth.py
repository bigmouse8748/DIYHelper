"""
Authentication Module - JWT token management
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid
import logging

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..config import settings
from ..database import get_db
from ..models.user import User, RefreshToken
from .security import PasswordService

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


class AuthService:
    """JWT Authentication Service"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire = timedelta(minutes=settings.access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=settings.refresh_token_expire_days)
    
    async def authenticate_user(
        self, 
        email: str, 
        password: str,
        db: AsyncSession
    ) -> Optional[User]:
        """Authenticate user with email and password"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
            
        if not PasswordService.verify_password(password, user.password_hash):
            return None
            
        return user
    
    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""        
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "user_type": str(user.user_type),
            "exp": datetime.utcnow() + self.access_token_expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    async def create_refresh_token(
        self, 
        user: User,
        db: AsyncSession
    ) -> str:
        """Create and store refresh token"""
        jti = str(uuid.uuid4())
        expires_at = datetime.utcnow() + self.refresh_token_expire
        
        # Create refresh token record
        refresh_token = RefreshToken(
            jti=jti,
            user_id=user.id,
            expires_at=expires_at
        )
        db.add(refresh_token)
        await db.commit()
        
        # Create JWT
        payload = {
            "sub": str(user.id),
            "jti": jti,
            "exp": expires_at,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    async def verify_token(
        self, 
        token: str,
        token_type: str = "access"
    ) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Check token type
            if payload.get("type") != token_type:
                return None
                
            return payload
            
        except JWTError as e:
            logger.error(f"JWT verification error: {str(e)}")
            return None
    
    async def refresh_access_token(
        self,
        refresh_token: str,
        db: AsyncSession
    ) -> Optional[tuple[str, str]]:
        """Use refresh token to get new access token"""
        payload = await self.verify_token(refresh_token, "refresh")
        if not payload:
            return None
        
        # Check if refresh token is revoked
        jti = payload.get("jti")
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.jti == jti,
                RefreshToken.is_revoked == False
            )
        )
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            return None
        
        # Get user
        result = await db.execute(
            select(User).where(User.id == int(payload["sub"]))
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        
        # Create new tokens
        new_access_token = self.create_access_token(user)
        new_refresh_token = await self.create_refresh_token(user, db)
        
        # Revoke old refresh token
        token_record.is_revoked = True
        token_record.revoked_at = datetime.utcnow()
        await db.commit()
        
        return new_access_token, new_refresh_token
    
    async def revoke_refresh_token(
        self,
        refresh_token: str,
        db: AsyncSession
    ) -> bool:
        """Revoke a refresh token"""
        try:
            payload = jwt.decode(
                refresh_token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            jti = payload.get("jti")
            
            if jti:
                result = await db.execute(
                    select(RefreshToken).where(RefreshToken.jti == jti)
                )
                token_record = result.scalar_one_or_none()
                
                if token_record:
                    token_record.is_revoked = True
                    token_record.revoked_at = datetime.utcnow()
                    await db.commit()
                    return True
                    
        except JWTError:
            pass
            
        return False


# Global auth service instance
auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    
    payload = await auth_service.verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(payload["sub"])
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to require admin privileges"""
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def get_optional_user(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get user if authenticated, otherwise return None"""
    if not authorization:
        return None
        
    try:
        token = authorization.credentials
        payload = await auth_service.verify_token(token, "access")
        
        if not payload:
            return None
            
        user_id = int(payload["sub"])
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        return user if user and user.is_active else None
        
    except Exception:
        return None