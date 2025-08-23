"""
完整重建数据库脚本
清空现有数据库并使用当前SQLAlchemy模型重新创建所有表
"""
import asyncio
import asyncpg
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.base import Base
# 导入所有模型以确保它们被注册到Base.metadata中
from app.models.user import User, UserSession, RefreshToken
# 导入其他模型（如果有的话）
# from app.models.other_models import ...
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库连接配置 - 使用环境变量
DATABASE_URL = os.getenv("DATABASE_URL") or f"postgresql://{os.getenv('DB_USER', 'dbadmin')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'cheasydiy')}"

if not os.getenv("DB_PASSWORD"):
    print("❌ 错误: DB_PASSWORD 环境变量未设置")
    print("   请设置环境变量: export DB_PASSWORD=your_password")
    exit(1)

async def rebuild_database():
    """完整重建数据库"""
    
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
    
    logger.info(f"连接到数据库: {host}:{port}/{db_name}")
    
    try:
        # 直接连接到PostgreSQL
        conn = await asyncpg.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db_name
        )
        
        logger.info("数据库连接成功")
        
        # 第一步：删除所有现有的表
        logger.info("正在删除现有表...")
        
        # 获取所有表名
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """)
        
        table_names = [table['table_name'] for table in tables]
        logger.info(f"找到 {len(table_names)} 个表: {table_names}")
        
        # 删除所有表（使用CASCADE删除依赖）
        for table_name in table_names:
            try:
                await conn.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
                logger.info(f"✓ 删除表: {table_name}")
            except Exception as e:
                logger.warning(f"删除表 {table_name} 失败: {e}")
        
        # 关闭asyncpg连接
        await conn.close()
        logger.info("现有表删除完成")
        
        # 第二步：使用SQLAlchemy重新创建所有表
        logger.info("正在使用SQLAlchemy重新创建表...")
        
        # 创建异步引擎
        async_engine = create_async_engine(
            DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
            echo=True
        )
        
        # 创建所有表
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ 所有表重新创建完成")
        
        # 验证表结构
        logger.info("验证新表结构...")
        conn = await asyncpg.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db_name
        )
        
        # 检查users表的列
        users_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        
        logger.info("Users表结构:")
        for col in users_columns:
            logger.info(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # 检查所有表
        new_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        new_table_names = [table['table_name'] for table in new_tables]
        logger.info(f"✅ 重建完成! 新建表: {new_table_names}")
        
        await conn.close()
        await async_engine.dispose()
        
        logger.info("🎉 数据库重建完成!")
        
    except Exception as e:
        logger.error(f"数据库重建失败: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("⚠️  警告: 此脚本将删除所有现有数据!")
    print("⚠️  Warning: This script will DELETE ALL existing data!")
    print()
    
    confirm = input("确认要继续吗? 输入 'YES' 继续: ")
    if confirm == "YES":
        asyncio.run(rebuild_database())
    else:
        print("操作已取消")