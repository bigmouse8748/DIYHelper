"""
Create a test user for the application
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import PasswordService

async def create_test_user():
    """Create a test user with known credentials"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if user already exists
            from sqlalchemy import select
            stmt = select(User).where(User.email == "test@example.com")
            result = await db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("Test user already exists!")
                print("Email: test@example.com")
                print("Password: Test123!")
                return
            
            # Create test user
            test_user = User(
                username="testuser",
                email="test@example.com",
                password_hash=PasswordService.hash_password("Test123!"),
                full_name="Test User",
                user_type="free",
                is_active=True,
                email_verified=True
            )
            
            db.add(test_user)
            await db.commit()
            print("Test user created successfully!")
            print("Email: test@example.com")
            print("Password: Test123!")
            
        except Exception as e:
            print(f"Error creating test user: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(create_test_user())