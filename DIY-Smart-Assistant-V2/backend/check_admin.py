#!/usr/bin/env python3
"""
Check for admin user and create one if doesn't exist
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import PasswordService


async def check_and_create_admin():
    """Check if admin user exists, create if not"""
    async with AsyncSessionLocal() as db:
        # Check if admin user exists
        result = await db.execute(
            select(User).where(User.email == "admin@diyassistant.com")
        )
        admin_user = result.scalar_one_or_none()
        
        if admin_user:
            print(f"Admin user found:")
            print(f"  Email: {admin_user.email}")
            print(f"  Username: {admin_user.username}")
            print(f"  User Type: {admin_user.user_type}")
            print(f"  Active: {admin_user.is_active}")
            
            # Update user_type to admin if needed
            if admin_user.user_type != "admin":
                print(f"  Updating user_type from '{admin_user.user_type}' to 'admin'")
                admin_user.user_type = "admin"
                await db.commit()
                
        else:
            print("Admin user not found. Creating admin user...")
            # Create admin user
            admin_user = User(
                username="admin",
                email="admin@diyassistant.com",
                password_hash=PasswordService.hash_password("admin123"),
                full_name="Admin User",
                user_type="admin",
                is_active=True,
                email_verified=True
            )
            
            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)
            
            print(f"Admin user created:")
            print(f"  Email: admin@diyassistant.com")
            print(f"  Password: admin123")
            print(f"  User Type: {admin_user.user_type}")
            
        print("\nAdmin user is ready for login!")


if __name__ == "__main__":
    asyncio.run(check_and_create_admin())