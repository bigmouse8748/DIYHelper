"""
Reset admin user password for testing
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import PasswordService
from sqlalchemy import select

async def reset_admin_user():
    """Reset admin user with correct credentials"""
    async with AsyncSessionLocal() as db:
        try:
            # Find the existing admin user
            stmt = select(User).where(User.email == "haozhouneu@gmail.com")
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                print("Found existing admin user - updating credentials")
                # Update the existing user
                user.password_hash = PasswordService.hash_password("admin123")
                user.email_verified = True
                user.is_active = True
                user.failed_login_attempts = 0
                user.locked_until = None
                user.user_type = "admin"  # Ensure it's admin
                
                await db.commit()
                print("Admin user updated successfully!")
                print(f"User ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Type: {user.user_type}")
            else:
                print("Admin user not found")
                
            print("Admin login credentials:")
            print("Email: haozhouneu@gmail.com")
            print("Password: admin123")
            
        except Exception as e:
            print(f"Error: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(reset_admin_user())