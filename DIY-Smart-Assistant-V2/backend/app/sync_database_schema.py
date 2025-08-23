"""
数据库Schema自动同步脚本
在每次部署时自动同步本地SQLAlchemy模型到RDS数据库
"""
import asyncio
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, inspect
from .models.base import Base
from .models.user import User, UserSession, RefreshToken
from .config import settings

logger = logging.getLogger(__name__)

async def sync_database_schema():
    """
    同步数据库schema到生产环境
    - 如果是测试/开发阶段，直接重建所有表
    - 如果表不存在，创建新表
    - 如果表存在但列缺失，添加缺失的列
    """
    
    logger.info("开始数据库Schema同步...")
    
    # 创建数据库引擎
    database_url = settings.database_url
    if database_url.startswith("sqlite"):
        logger.info("检测到SQLite数据库，跳过同步")
        return
    
    # 转换为async URL
    async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(async_url, echo=False)  # 生产环境关闭SQL日志
    
    try:
        # 检查是否为测试环境 - 如果是测试环境，直接重建
        environment = os.getenv("ENVIRONMENT", "development")
        is_production = environment == "production"
        
        if not is_production:
            logger.info("检测到非生产环境，执行完整schema重建...")
            
            # 删除所有表并重建（仅在测试环境）
            async with engine.begin() as conn:
                # 删除所有表
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("删除所有现有表")
                
                # 重新创建所有表
                await conn.run_sync(Base.metadata.create_all)
                logger.info("重新创建所有表")
                
            logger.info("✅ 数据库Schema完全重建完成")
        
        else:
            logger.info("生产环境模式 - 执行增量Schema更新...")
            
            async with engine.begin() as conn:
                # 确保表存在
                await conn.run_sync(Base.metadata.create_all)
                logger.info("确保所有表存在")
                
                # 检查并添加缺失的列（生产环境的安全做法）
                # 由于asyncpg的限制，我们使用同步连接来检查schema
                sync_engine = engine.sync_engine
                inspector = inspect(sync_engine)
                
                for table_name, table in Base.metadata.tables.items():
                    if inspector.has_table(table_name):
                        existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
                        
                        for column in table.columns:
                            if column.name not in existing_columns:
                                # 构建ADD COLUMN语句 - 使用PostgreSQL的IF NOT EXISTS
                                column_type = column.type.compile(engine.dialect)
                                nullable = "" if column.nullable else " NOT NULL"
                                default = ""
                                if column.default is not None:
                                    if hasattr(column.default, 'arg'):
                                        if isinstance(column.default.arg, str):
                                            default = f" DEFAULT '{column.default.arg}'"
                                        else:
                                            default = f" DEFAULT {column.default.arg}"
                                    elif hasattr(column.default, 'name'):
                                        default = f" DEFAULT {column.default.name}()"
                                
                                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column.name} {column_type}{default}{nullable}"
                                
                                try:
                                    await conn.execute(text(alter_sql))
                                    logger.info(f"添加列: {table_name}.{column.name}")
                                except Exception as e:
                                    logger.warning(f"添加列失败 {table_name}.{column.name}: {e}")
                    else:
                        logger.info(f"表 {table_name} 不存在，已通过 create_all 创建")
        
        # 验证最终结果
        logger.info("验证数据库结构...")
        async with engine.begin() as conn:
            # 检查users表结构
            try:
                result = await conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position
                """))
                
                columns = result.fetchall()
                logger.info(f"Users表包含 {len(columns)} 列")
                
                # 验证关键列是否存在
                column_names = [col[0] for col in columns]
                required_columns = ['id', 'username', 'email', 'password_hash', 'user_type', 'is_active', 'email_verified']
                
                for req_col in required_columns:
                    if req_col in column_names:
                        logger.info(f"  ✓ {req_col}")
                    else:
                        logger.error(f"  ✗ 缺失必需列: {req_col}")
                        
            except Exception as e:
                logger.warning(f"验证数据库结构时出错: {e}")
        
        logger.info("🎉 数据库Schema同步完成!")
        
    except Exception as e:
        logger.error(f"Schema同步失败: {e}")
        raise
    finally:
        await engine.dispose()

async def test_database_connection():
    """测试数据库连接"""
    database_url = settings.database_url
    if database_url.startswith("sqlite"):
        logger.info("SQLite数据库连接测试跳过")
        return True
    
    async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(async_url)
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("✅ 数据库连接测试成功")
        return True
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        return False
    finally:
        await engine.dispose()