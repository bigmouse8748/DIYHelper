#!/usr/bin/env python3
"""
查询RDS数据库中的用户信息
"""
import asyncio
import asyncpg
import os
from datetime import datetime

async def query_users():
    """查询用户信息"""
    print("=== RDS Database User Query ===")
    
    try:
        # 连接数据库
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        print("✅ Connected to database successfully")
        
        # 检查表结构
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"\n📋 Database Tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # 检查users表是否存在
        if not any(t['table_name'] == 'users' for t in tables):
            print("❌ Users table not found!")
            return
        
        # 查询用户统计
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN email_verified THEN 1 END) as verified_users,
                COUNT(CASE WHEN is_active THEN 1 END) as active_users,
                COUNT(CASE WHEN user_type = 'admin' THEN 1 END) as admin_users
            FROM users
        """)
        
        print(f"\n📊 User Statistics:")
        print(f"  Total users: {stats['total_users']}")
        print(f"  Verified users: {stats['verified_users']}")
        print(f"  Active users: {stats['active_users']}")
        print(f"  Admin users: {stats['admin_users']}")
        
        # 查询前10个用户
        users = await conn.fetch("""
            SELECT id, username, email, full_name, user_type, is_active, email_verified, created_at
            FROM users 
            ORDER BY id 
            LIMIT 10
        """)
        
        print(f"\n👤 First 10 Users:")
        if users:
            print("ID | Username      | Email                 | Type | Active | Verified | Created")
            print("-" * 80)
            for user in users:
                created = user['created_at'].strftime('%Y-%m-%d') if user['created_at'] else 'N/A'
                active = "Yes" if user['is_active'] else "No"
                verified = "Yes" if user['email_verified'] else "No"
                print(f"{user['id']:<2} | {user['username']:<12} | {user['email']:<20} | {user['user_type']:<4} | {active:<6} | {verified:<8} | {created}")
        else:
            print("  No users found")
        
        # 查询最近注册的用户
        recent_users = await conn.fetch("""
            SELECT username, email, created_at, user_type
            FROM users 
            WHERE created_at IS NOT NULL
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print(f"\n🆕 Recent Users:")
        if recent_users:
            for user in recent_users:
                created = user['created_at'].strftime('%Y-%m-%d %H:%M') if user['created_at'] else 'N/A'
                print(f"  - {user['username']} ({user['email']}) - {user['user_type']} - {created}")
        else:
            print("  No recent users found")
        
        await conn.close()
        print("\n✅ Query completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(query_users())