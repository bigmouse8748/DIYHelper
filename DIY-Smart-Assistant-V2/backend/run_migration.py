"""
Run database migration to add missing columns
This should be run inside the container where the app is deployed
"""
import asyncio
from app.database import engine
from sqlalchemy import text

async def run_migration():
    """Add missing columns to users table"""
    async with engine.begin() as conn:
        print("Adding missing columns to users table...")
        
        # Add missing columns one by one
        migrations = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(50)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS location VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verify_token VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_expires TIMESTAMP",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP"
        ]
        
        for migration in migrations:
            try:
                await conn.execute(text(migration))
                print(f"✓ Executed: {migration}")
            except Exception as e:
                print(f"✗ Failed: {migration}")
                print(f"  Error: {e}")
        
        print("Migration completed!")

if __name__ == "__main__":
    asyncio.run(run_migration())