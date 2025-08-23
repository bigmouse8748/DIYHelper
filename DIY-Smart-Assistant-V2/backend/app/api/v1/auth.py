"""
Authentication API endpoints
"""

from datetime import datetime
from typing import Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...database import get_db
from ...models.user import User, UserSession
from ...schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, RefreshTokenRequest
from ...schemas.common import MessageResponse
from ...core.auth import auth_service, get_current_user
from ...core.security import PasswordService
from ...core.email import email_service
from ...config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.options("/login")
async def login_options():
    """Handle OPTIONS request for login endpoint"""
    return Response(status_code=200)

@router.options("/register")
async def register_options():
    """Handle OPTIONS request for register endpoint"""
    return Response(status_code=200)

@router.options("/refresh")
async def refresh_options():
    """Handle OPTIONS request for refresh endpoint"""
    return Response(status_code=200)

@router.options("/logout")
async def logout_options():
    """Handle OPTIONS request for logout endpoint"""
    return Response(status_code=200)

@router.options("/verify-email")
async def verify_email_options():
    """Handle OPTIONS request for verify-email endpoint"""
    return Response(status_code=200)


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new user"""
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = PasswordService.hash_password(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password_hash=hashed_password,
        email_verify_token=PasswordService.generate_token()
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Send verification email
    logger.info(f"Attempting to send verification email to {user.email}")
    logger.info(f"User verification token: {user.email_verify_token}")
    logger.info(f"Email service configured: {email_service.is_configured()}")
    
    try:
        result = await email_service.send_verification_email(
            to_email=user.email,
            username=user.username,
            verification_token=user.email_verify_token,
            base_url=settings.base_url
        )
        logger.info(f"Verification email sent to {user.email}, result: {result}")
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        logger.exception("Email sending exception details:")
        # Don't fail registration if email sending fails
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Login with email and password"""
    # Authenticate user
    user = await auth_service.authenticate_user(
        credentials.email,
        credentials.password,
        db
    )
    
    if not user:
        # Increment failed login attempts for the email
        result = await db.execute(
            select(User).where(User.email == credentials.email)
        )
        failed_user = result.scalar_one_or_none()
        if failed_user:
            failed_user.failed_login_attempts += 1
            await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked due to too many failed login attempts"
        )
    
    # Check if email is verified
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address before logging in. Check your inbox for a verification email."
        )
    
    # Create tokens
    access_token = auth_service.create_access_token(user)
    refresh_token = await auth_service.create_refresh_token(user, db)
    
    # Update user login info
    user.last_login = datetime.utcnow()
    user.failed_login_attempts = 0
    user.locked_until = None
    
    # Create session record
    session = UserSession(
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    db.add(session)
    
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.from_orm(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Refresh access token using refresh token"""
    result = await auth_service.refresh_access_token(
        refresh_data.refresh_token,
        db
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token, refresh_token = result
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Logout and revoke refresh token"""
    success = await auth_service.revoke_refresh_token(
        refresh_data.refresh_token,
        db
    )
    
    return MessageResponse(
        message="Logged out successfully",
        success=success
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user information"""
    return current_user


@router.get("/verify")
async def verify_email_get(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Verify user email using verification token (GET request from email link)"""
    try:
        # Find user by verification token
        result = await db.execute(
            select(User).where(User.email_verify_token == token)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        if user.email_verified:
            return {
                "message": "Email already verified. You can now log in.",
                "success": True,
                "verified": True,
                "username": user.username
            }
        
        # Verify the email
        user.email_verified = True
        user.email_verify_token = None
        
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Email verified successfully for user {user.username}")
        
        return {
            "message": "Email verified successfully! You can now log in to your account.",
            "success": True,
            "verified": True,
            "username": user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed. Please try again or contact support."
        )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Verify email with token"""
    result = await db.execute(
        select(User).where(
            User.email_verify_token == token,
            User.email_verified == False
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    user.email_verified = True
    user.email_verify_token = None
    await db.commit()
    
    return MessageResponse(
        message="Email verified successfully",
        success=True
    )