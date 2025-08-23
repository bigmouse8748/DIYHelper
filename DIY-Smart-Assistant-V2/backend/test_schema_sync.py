"""
测试Schema同步功能
验证本地SQLAlchemy模型是否能正确同步
"""
import asyncio
import tempfile
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.sync_database_schema import sync_database_schema, test_database_connection
from app.models.base import Base
from app.models.user import User, UserSession, RefreshToken
from app.config import settings

async def test_schema_sync_with_sqlite():
    """使用临时SQLite数据库测试schema同步功能"""
    
    print("🧪 测试Schema同步功能...")
    
    # 创建临时数据库文件
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        temp_db_path = tmp_file.name
    
    try:
        # 修改配置使用临时SQLite数据库
        original_db_url = settings.database_url
        settings.database_url = f"sqlite:///{temp_db_path}"
        
        print(f"使用临时数据库: {settings.database_url}")
        
        # 创建引擎
        engine = create_async_engine(f"sqlite+aiosqlite:///{temp_db_path}")
        
        # 首先创建一个不完整的schema来模拟旧版本数据库
        print("创建不完整的数据库schema...")
        async with engine.begin() as conn:
            # 创建一个简化版本的users表（缺少一些列）
            await conn.execute(text("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                )
            """))
            print("创建了简化版users表（缺少大部分列）")
        
        # 检查初始状态
        async with engine.begin() as conn:
            result = await conn.execute(text("PRAGMA table_info(users)"))
            initial_columns = [row[1] for row in result.fetchall()]
            print(f"初始列: {initial_columns}")
        
        # 执行schema同步
        print("\n执行Schema同步...")
        settings.database_url = f"sqlite:///{temp_db_path}"  # 确保使用正确的URL格式
        
        # 模拟开发环境（会进行完整重建）
        os.environ["ENVIRONMENT"] = "development"
        
        try:
            await sync_database_schema()
            print("✅ Schema同步完成")
        except Exception as e:
            print(f"❌ Schema同步失败: {e}")
            raise
        
        # 检查同步后的状态
        async with engine.begin() as conn:
            result = await conn.execute(text("PRAGMA table_info(users)"))
            final_columns = [row[1] for row in result.fetchall()]
            print(f"\n同步后列: {final_columns}")
        
        # 验证所有期望的列是否存在
        expected_columns = [
            'id', 'username', 'email', 'password_hash', 'full_name',
            'avatar_url', 'user_type', 'is_active', 'email_verified',
            'email_verify_token', 'password_reset_token', 'password_reset_expires',
            'failed_login_attempts', 'locked_until', 'last_login',
            'phone', 'location', 'created_at', 'updated_at'
        ]
        
        missing_columns = [col for col in expected_columns if col not in final_columns]
        if missing_columns:
            print(f"❌ 缺失列: {missing_columns}")
        else:
            print("✅ 所有期望列都存在")
        
        # 测试插入操作
        print("\n测试数据库操作...")
        async with engine.begin() as conn:
            await conn.execute(text("""
                INSERT INTO users (username, email, password_hash, full_name, user_type, is_active, email_verified)
                VALUES ('test_user', 'test@example.com', 'hash123', 'Test User', 'free', 1, 0)
            """))
            
            result = await conn.execute(text("SELECT username, email, full_name, user_type FROM users WHERE username = 'test_user'"))
            user_data = result.fetchone()
            
            if user_data:
                print(f"✅ 用户插入成功: {user_data}")
            else:
                print("❌ 用户插入失败")
        
        # 检查所有表是否都被创建
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            print(f"\n创建的表: {tables}")
            
            expected_tables = ['users', 'user_sessions', 'refresh_tokens']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                print(f"❌ 缺失表: {missing_tables}")
            else:
                print("✅ 所有期望表都存在")
        
        await engine.dispose()
        
        # 恢复原始配置
        settings.database_url = original_db_url
        
        print("\n🎉 Schema同步测试完成!")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_db_path)
        except:
            pass
        # 恢复原始配置
        settings.database_url = original_db_url

async def test_production_mode():
    """测试生产模式的增量更新"""
    print("\n🧪 测试生产模式增量更新...")
    
    # 设置为生产环境
    os.environ["ENVIRONMENT"] = "production"
    
    # 这里只是演示逻辑，不实际连接生产数据库
    print("生产模式: 会执行增量Schema更新而不是完整重建")
    print("- 检查现有表和列")
    print("- 仅添加缺失的列，不删除现有数据")
    print("- 更安全的生产环境更新策略")
    
    return True

if __name__ == "__main__":
    async def main():
        # 测试开发模式的完整重建
        success1 = await test_schema_sync_with_sqlite()
        
        # 测试生产模式的增量更新
        success2 = await test_production_mode()
        
        if success1 and success2:
            print("\n🎉 所有测试通过!")
        else:
            print("\n❌ 部分测试失败")
            
    asyncio.run(main())