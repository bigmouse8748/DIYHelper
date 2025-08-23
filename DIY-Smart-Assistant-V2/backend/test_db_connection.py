import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_connection():
    database_url = os.getenv("DATABASE_URL", "postgresql://dbadmin:ChEasyDiy2024!@cheasydiy-production-db.c9sieeomsxup.us-east-1.rds.amazonaws.com:5432/cheasydiy")
    print(f"Testing connection...")
    
    try:
        async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        engine = create_async_engine(async_url, echo=True, pool_pre_ping=True)
        
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Connection successful! Result: {result.scalar()}")
            
        await engine.dispose()
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
