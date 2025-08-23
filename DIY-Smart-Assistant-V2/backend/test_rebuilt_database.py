"""
测试重建后的数据库
验证所有表和列是否正确创建
"""
import asyncio
import asyncpg
import os
from app.config import settings

async def test_database():
    """测试数据库结构和基本操作"""
    
    # 数据库连接配置
    DATABASE_URL = settings.database_url
    
    # 解析数据库URL
    if DATABASE_URL.startswith("postgresql://"):
        db_url = DATABASE_URL.replace("postgresql://", "")
    else:
        db_url = DATABASE_URL
    
    # 提取连接信息
    auth, rest = db_url.split("@")
    user, password = auth.split(":")
    host_port, db_name = rest.split("/")
    host, port = host_port.split(":")
    
    print(f"连接到数据库: {host}:{port}/{db_name}")
    
    try:
        # 连接数据库
        conn = await asyncpg.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db_name
        )
        
        print("✅ 数据库连接成功")
        
        # 检查所有表
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        table_names = [table['table_name'] for table in tables]
        print(f"\n📋 数据库表 ({len(table_names)}):")
        for table_name in table_names:
            print(f"  - {table_name}")
        
        # 详细检查users表
        print("\n👤 Users表结构:")
        users_columns = await conn.fetch("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable, 
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        
        for col in users_columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            data_type = col['data_type']
            if col['character_maximum_length']:
                data_type += f"({col['character_maximum_length']})"
            
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  - {col['column_name']:<25} {data_type:<20} {nullable:<10}{default}")
        
        # 测试插入一个测试用户
        print("\n🧪 测试用户操作...")
        
        # 检查是否已有测试用户
        existing_user = await conn.fetchrow(
            "SELECT id, username, email FROM users WHERE username = $1", 
            "test_rebuild_user"
        )
        
        if existing_user:
            print(f"  - 找到现有测试用户: {existing_user['username']} ({existing_user['email']})")
            user_id = existing_user['id']
        else:
            # 插入测试用户
            user_id = await conn.fetchval("""
                INSERT INTO users (
                    username, email, password_hash, full_name, 
                    user_type, is_active, email_verified
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """, "test_rebuild_user", "test@rebuild.com", "test_hash", 
                "Test Rebuild User", "free", True, False)
            
            print(f"  - ✅ 创建测试用户成功: ID {user_id}")
        
        # 验证用户数据
        user = await conn.fetchrow("""
            SELECT username, email, full_name, user_type, is_active, 
                   email_verified, created_at, updated_at
            FROM users WHERE id = $1
        """, user_id)
        
        print(f"  - 用户信息: {user['username']} - {user['full_name']} ({user['user_type']})")
        print(f"  - 活跃状态: {user['is_active']}, 邮箱验证: {user['email_verified']}")
        print(f"  - 创建时间: {user['created_at']}")
        
        # 测试用户会话表
        print("\n📝 测试用户会话...")
        session_id = await conn.fetchval("""
            INSERT INTO user_sessions (user_id, ip_address, user_agent)
            VALUES ($1, $2, $3)
            RETURNING id
        """, user_id, "127.0.0.1", "Test Agent")
        
        print(f"  - ✅ 创建用户会话成功: ID {session_id}")
        
        # 清理测试数据
        await conn.execute("DELETE FROM user_sessions WHERE id = $1", session_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)
        print("  - 🧹 测试数据清理完成")
        
        await conn.close()
        print("\n🎉 数据库测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database())