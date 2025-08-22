"""
Reset test user with correct credentials and verification status
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import PasswordService
from sqlalchemy import select

async def reset_test_user():
    """Reset test user with correct credentials"""
    async with AsyncSessionLocal() as db:
        try:
            # Find the existing test user
            stmt = select(User).where(User.email == "test@example.com")
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                print("Found existing test user - updating credentials")
                # Update the existing user
                user.password_hash = PasswordService.hash_password("Test123!")
                user.email_verified = True
                user.is_active = True
                user.failed_login_attempts = 0
                user.locked_until = None
                
                await db.commit()
                print("Test user updated successfully!")
            else:
                print("Creating new test user")
                # Create new test user
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
            print(f"Error: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(reset_test_user())