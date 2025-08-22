"""
Create an admin user for the application
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import PasswordService

async def create_admin_user():
    """Create an admin user with known credentials"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if admin user already exists
            from sqlalchemy import select
            stmt = select(User).where(User.email == "admin@example.com")
            result = await db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # Update existing user to be admin
                existing_user.user_type = "admin"
                existing_user.is_active = True
                existing_user.email_verified = True
                await db.commit()
                print("Admin user updated!")
                print("Email: admin@example.com")
                print("Password: Admin123!")
                return
            
            # Create admin user
            admin_user = User(
                username="adminuser",
                email="admin@example.com",
                password_hash=PasswordService.hash_password("Admin123!"),
                full_name="Admin User",
                user_type="admin",
                is_active=True,
                email_verified=True
            )
            
            db.add(admin_user)
            await db.commit()
            print("Admin user created successfully!")
            print("Email: admin@example.com")
            print("Password: Admin123!")
            
        except Exception as e:
            print(f"Error creating admin user: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(create_admin_user())