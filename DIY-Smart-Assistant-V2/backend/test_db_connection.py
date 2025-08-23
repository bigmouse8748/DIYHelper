#!/usr/bin/env python3
"""
数据库连接测试脚本
用于诊断ECS任务中的数据库连接问题
"""
import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_connection():
    """测试数据库连接"""
    try:
        # 获取环境变量
        database_url = os.environ.get('DATABASE_URL', 'NOT_SET')
        environment = os.environ.get('ENVIRONMENT', 'development')
        
        logger.info(f"Environment: {environment}")
        logger.info(f"Database URL: {database_url}")
        
        if database_url == 'NOT_SET':
            logger.error("DATABASE_URL environment variable not set!")
            return False
            
        # 转换为异步URL
        if database_url.startswith("postgresql://"):
            async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            logger.error(f"Unsupported database URL format: {database_url}")
            return False
            
        logger.info(f"Async URL: {async_url}")
        
        # 创建引擎
        engine = create_async_engine(
            async_url,
            echo=True,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={
                "server_settings": {
                    "application_name": "DIY_Assistant_Health_Check",
                }
            }
        )
        
        # 测试连接
        logger.info("Testing database connection...")
        async with engine.begin() as conn:
            from sqlalchemy import text
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            logger.info(f"Database connection successful! Result: {row}")
            
        await engine.dispose()
        logger.info("Database connection test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_database_connection())
    sys.exit(0 if success else 1)