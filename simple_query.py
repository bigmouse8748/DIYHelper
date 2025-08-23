#!/usr/bin/env python3
import asyncio
import asyncpg
import os

async def simple_query():
    try:
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'cheasydiy-production-db.c9sieeomsxup.us-east-1.rds.amazonaws.com'),
            port=int(os.getenv('DB_PORT', 5432)),
            user=os.getenv('DB_USER', 'dbadmin'),
            password=os.getenv('DB_PASSWORD', 'ChEasyDiy2024!'),
            database=os.getenv('DB_NAME', 'cheasydiy')
        )
        
        print("=== Database Connection Successful ===")
        
        # 查询用户数量
        count = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"Total users: {count}")
        
        # 查询前5个用户
        if count > 0:
            users = await conn.fetch("""
                SELECT id, username, email, user_type, is_active, created_at 
                FROM users 
                ORDER BY id 
                LIMIT 5
            """)
            print("\nFirst 5 users:")
            for user in users:
                print(f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}, Type: {user['user_type']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(simple_query())