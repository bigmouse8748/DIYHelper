"""
Add missing columns to existing database
Run this script to update the database schema
"""
import asyncio
import asyncpg
import os

async def add_missing_columns():
    # Database connection details
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dbadmin:ChEasyDiy2024!@cheasydiy-production-db.c9sieeomsxup.us-east-1.rds.amazonaws.com:5432/cheasydiy")
    
    # Parse connection URL
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "")
    
    # Extract components
    auth, rest = DATABASE_URL.split("@")
    user, password = auth.split(":")
    host_port, db = rest.split("/")
    host, port = host_port.split(":")
    
    print(f"Connecting to database at {host}:{port}/{db}")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db
        )
        
        print("Connected to database")
        
        # Check which columns exist
        columns = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """)
        
        existing_columns = [col['column_name'] for col in columns]
        print(f"Existing columns: {existing_columns}")
        
        # Add missing columns
        missing_columns = []
        
        if 'full_name' not in existing_columns:
            missing_columns.append(('full_name', 'VARCHAR(255)'))
        
        if 'phone' not in existing_columns:
            missing_columns.append(('phone', 'VARCHAR(50)'))
            
        if 'location' not in existing_columns:
            missing_columns.append(('location', 'VARCHAR(255)'))
            
        if 'avatar_url' not in existing_columns:
            missing_columns.append(('avatar_url', 'VARCHAR(500)'))
            
        if 'email_verify_token' not in existing_columns:
            missing_columns.append(('email_verify_token', 'VARCHAR(255)'))
            
        if 'password_reset_token' not in existing_columns:
            missing_columns.append(('password_reset_token', 'VARCHAR(255)'))
            
        if 'password_reset_expires' not in existing_columns:
            missing_columns.append(('password_reset_expires', 'TIMESTAMP'))
            
        if 'failed_login_attempts' not in existing_columns:
            missing_columns.append(('failed_login_attempts', 'INTEGER DEFAULT 0'))
            
        if 'locked_until' not in existing_columns:
            missing_columns.append(('locked_until', 'TIMESTAMP'))
            
        if 'last_login' not in existing_columns:
            missing_columns.append(('last_login', 'TIMESTAMP'))
        
        # Execute ALTER TABLE commands
        for column_name, column_type in missing_columns:
            query = f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
            print(f"Adding column: {column_name}")
            await conn.execute(query)
            print(f"✓ Added {column_name}")
        
        if not missing_columns:
            print("All columns already exist!")
        else:
            print(f"\n✅ Successfully added {len(missing_columns)} missing columns")
        
        # Close connection
        await conn.close()
        print("Database connection closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_missing_columns())