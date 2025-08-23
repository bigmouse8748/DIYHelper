"""
User management API endpoints
"""

from typing import Any, Optional
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from passlib.context import CryptContext
from pydantic import BaseModel, Field

from ...database import get_db
from ...models.user import User
from ...schemas.user import (
    UserResponse, 
    UserUpdate, 
    UserListResponse, 
    UserCreateAdmin
)
from ...core.auth import get_current_user, require_admin
from ...core.security import PasswordService

router = APIRouter()


@router.options("/admin/users")
async def admin_users_options():
    """Handle OPTIONS request for admin users endpoint"""
    return Response(status_code=200)

@router.options("/admin/users/{user_id}/verify-email")
async def admin_verify_email_options(user_id: int):
    """Handle OPTIONS request for admin verify-email endpoint"""
    return Response(status_code=200)


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user profile"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    full_name: str = None,
    location: str = None,
    phone: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update user profile"""
    if full_name:
        current_user.full_name = full_name
    if location:
        current_user.location = location
    if phone:
        current_user.phone = phone
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.get("/permissions")
async def get_user_permissions(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get user permissions based on user type"""
    return {
        "user_type": current_user.user_type,
        "permissions": current_user.get_permissions()
    }


# Admin-only endpoints
@router.get("/admin/users", response_model=UserListResponse)
async def get_all_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    user_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all users with pagination and filtering (Admin only)"""
    
    # Build query
    query = select(User)
    
    # Add search filter
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.full_name.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    # Add filters
    if user_type:
        query = query.where(User.user_type == user_type)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Add pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(User.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()
    
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total > 0 else 0
    )


@router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get user by ID (Admin only)"""
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/admin/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreateAdmin,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create new user (Admin only)"""
    
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
    
    # Create user
    hashed_password = PasswordService.hash_password(user_data.password)
    
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password_hash=hashed_password,
        user_type=user_data.user_type.value,
        is_active=user_data.is_active,
        email_verified=user_data.email_verified
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update user (Admin only)"""
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if email is being changed and already exists
    if user_data.email and user_data.email != user.email:
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check if username is being changed and already exists
    if user_data.username and user_data.username != user.username:
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update user fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(user, field):
            if field == "user_type" and value:
                setattr(user, field, value.value)
            else:
                setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user


@router.post("/admin/users/{user_id}/verify-email")
async def verify_user_email(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Manually verify user email (Admin only)"""
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already verified
    if user.email_verified:
        return {"message": "Email already verified", "success": True}
    
    # Verify email
    user.email_verified = True
    user.email_verify_token = None
    
    await db.commit()
    await db.refresh(user)
    
    return {"message": f"Email verified successfully for user {user.username}", "success": True}


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete user (Admin only)"""
    
    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete user
    await db.delete(user)
    await db.commit()
    
    return {"message": "User deleted successfully"}


class PasswordResetRequest(BaseModel):
    new_password: str = Field(..., min_length=8)


@router.put("/admin/users/{user_id}/password")
async def reset_user_password(
    user_id: int,
    password_data: PasswordResetRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Reset user password (Admin only)"""
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    hashed_password = PasswordService.hash_password(password_data.new_password)
    user.password_hash = hashed_password
    
    await db.commit()
    
    return {"message": "Password reset successfully"}