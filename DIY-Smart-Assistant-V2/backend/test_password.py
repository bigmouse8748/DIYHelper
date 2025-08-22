"""
Test password verification for test user
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import PasswordService
from sqlalchemy import select

async def test_password():
    """Test password verification"""
    async with AsyncSessionLocal() as db:
        try:
            # Find the test user
            stmt = select(User).where(User.email == "test@example.com")
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                print("Test user not found!")
                return
            
            print(f"User found: {user.email}")
            print(f"Username: {user.username}")
            print(f"Email verified: {user.email_verified}")
            print(f"Is active: {user.is_active}")
            print(f"User type: {user.user_type}")
            print(f"Password hash: {user.password_hash[:50]}...")
            
            # Test password verification
            test_password = "Test123!"
            is_valid = PasswordService.verify_password(test_password, user.password_hash)
            print(f"Password '{test_password}' is valid: {is_valid}")
            
            # Create a new hash and test it
            print("\nTesting new hash generation:")
            new_hash = PasswordService.hash_password(test_password)
            print(f"New hash: {new_hash[:50]}...")
            is_valid_new = PasswordService.verify_password(test_password, new_hash)
            print(f"New hash verification: {is_valid_new}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_password())