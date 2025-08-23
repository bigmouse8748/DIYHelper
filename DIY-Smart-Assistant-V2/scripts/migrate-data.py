#!/usr/bin/env python3
"""
数据迁移脚本：从本地SQLite迁移到AWS RDS PostgreSQL
"""
import asyncio
import asyncpg
import aiosqlite
import json
from typing import List, Dict, Any
import os
from datetime import datetime

# 配置
LOCAL_DB_PATH = "../backend/instance/app.db"  # 本地SQLite数据库路径
RDS_CONNECTION = {
    "host": os.getenv("DB_HOST", "cheasydiy-production-db.c9sieeomsxup.us-east-1.rds.amazonaws.com"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "cheasydiy"),
    "user": os.getenv("DB_USER", "dbadmin"),
    "password": os.getenv("DB_PASSWORD")  # 必须从环境变量获取，不能硬编码
}

async def migrate_table_data(table_name: str, sqlite_conn, pg_conn):
    """迁移单个表的数据"""
    print(f"🔄 迁移表: {table_name}")
    
    try:
        # 从SQLite读取数据
        async with sqlite_conn.execute(f"SELECT * FROM {table_name}") as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
        
        if not rows:
            print(f"⚠️  表 {table_name} 无数据，跳过")
            return
        
        # 构建PostgreSQL插入语句
        placeholders = ", ".join([f"${i+1}" for i in range(len(columns))])
        column_names = ", ".join(columns)
        
        insert_sql = f"""
        INSERT INTO {table_name} ({column_names}) 
        VALUES ({placeholders})
        ON CONFLICT DO NOTHING
        """
        
        # 批量插入到PostgreSQL
        await pg_conn.executemany(insert_sql, rows)
        print(f"✅ 表 {table_name} 迁移完成: {len(rows)} 条记录")
        
    except Exception as e:
        print(f"❌ 表 {table_name} 迁移失败: {e}")

async def main():
    """主迁移流程"""
    print("🚀 开始数据迁移: SQLite -> PostgreSQL")
    
    # 验证环境变量
    if not os.getenv("DB_PASSWORD"):
        print("❌ 错误: DB_PASSWORD 环境变量未设置")
        print("   请设置环境变量: export DB_PASSWORD=your_password")
        print("   或使用: DB_PASSWORD=your_password python migrate-data.py")
        return
    
    # 检查本地数据库是否存在
    if not os.path.exists(LOCAL_DB_PATH):
        print(f"❌ 本地数据库不存在: {LOCAL_DB_PATH}")
        return
    
    try:
        # 连接数据库
        sqlite_conn = await aiosqlite.connect(LOCAL_DB_PATH)
        pg_conn = await asyncpg.connect(**RDS_CONNECTION)
        
        print("✅ 数据库连接成功")
        
        # 按依赖顺序迁移表（避免外键约束问题）
        tables_order = [
            "users",  # 先迁移用户表
            "products",  # 再迁移产品表
            "product_analyses",
            "affiliate_clicks", 
            "recommendation_rules"
        ]
        
        for table in tables_order:
            await migrate_table_data(table, sqlite_conn, pg_conn)
        
        print("🎉 数据迁移完成！")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
    
    finally:
        if 'sqlite_conn' in locals():
            await sqlite_conn.close()
        if 'pg_conn' in locals():
            await pg_conn.close()

if __name__ == "__main__":
    asyncio.run(main())