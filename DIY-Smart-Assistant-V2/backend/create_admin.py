#!/usr/bin/env python3
"""
管理员账号创建和数据库管理脚本
"""

import asyncio
import sqlite3
import bcrypt
import secrets
from datetime import datetime
import shutil
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 数据库路径
DB_PATH = "diy_assistant.db"
BACKUP_PATH = f"diy_assistant_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def create_backup():
    """创建数据库备份"""
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✅ 数据库备份已创建: {BACKUP_PATH}")
        return True
    else:
        print("❌ 数据库文件不存在")
        return False

def view_users():
    """查看所有用户"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, user_type, is_active, email_verified, created_at, last_login 
            FROM users 
            ORDER BY id
        """)
        
        users = cursor.fetchall()
        
        print("\n📊 当前用户列表:")
        print("-" * 100)
        print(f"{'ID':<3} {'用户名':<15} {'邮箱':<25} {'类型':<10} {'激活':<5} {'验证':<5} {'创建时间':<20} {'最后登录':<20}")
        print("-" * 100)
        
        for user in users:
            user_id, username, email, user_type, is_active, email_verified, created_at, last_login = user
            is_active_str = "✅" if is_active else "❌"
            email_verified_str = "✅" if email_verified else "❌"
            last_login_str = last_login[:19] if last_login else "从未登录"
            created_at_str = created_at[:19] if created_at else ""
            
            print(f"{user_id:<3} {username:<15} {email:<25} {user_type:<10} {is_active_str:<5} {email_verified_str:<5} {created_at_str:<20} {last_login_str:<20}")
        
        print(f"\n总计: {len(users)} 个用户")
        conn.close()
        
    except Exception as e:
        print(f"❌ 查看用户失败: {e}")

def create_admin_user():
    """创建管理员账号"""
    admin_email = "admin@diyassistant.com"
    admin_username = "admin"
    admin_password = "DIYAdmin2025!"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查是否已存在管理员账号
        cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (admin_email, admin_username))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  管理员账号已存在 (ID: {existing[0]})")
            return
        
        # 创建密码哈希
        password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 生成邮箱验证令牌
        email_verify_token = secrets.token_urlsafe(32)
        
        # 插入管理员用户
        cursor.execute("""
            INSERT INTO users (
                username, email, password_hash, user_type, is_active, 
                email_verified, email_verify_token, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            admin_username, admin_email, password_hash, 'ADMIN', 1, 1, email_verify_token
        ))
        
        conn.commit()
        admin_id = cursor.lastrowid
        
        print(f"✅ 管理员账号创建成功!")
        print(f"   ID: {admin_id}")
        print(f"   用户名: {admin_username}")
        print(f"   邮箱: {admin_email}")
        print(f"   密码: {admin_password}")
        print(f"   类型: ADMIN")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 创建管理员账号失败: {e}")

def view_database_info():
    """查看数据库信息"""
    try:
        # 文件信息
        if os.path.exists(DB_PATH):
            file_size = os.path.getsize(DB_PATH)
            file_time = datetime.fromtimestamp(os.path.getmtime(DB_PATH))
            print(f"📁 数据库文件: {DB_PATH}")
            print(f"📏 文件大小: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print(f"🕒 修改时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("❌ 数据库文件不存在")
            return
        
        # 数据库表信息
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📋 数据库表 ({len(tables)} 个):")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   {table_name}: {count} 条记录")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 查看数据库信息失败: {e}")

def main():
    """主函数"""
    print("🔧 DIY Smart Assistant 数据库管理工具")
    print("=" * 50)
    
    # 查看数据库信息
    view_database_info()
    
    print("\n" + "=" * 50)
    
    # 创建备份
    backup_success = create_backup()
    
    print("\n" + "=" * 50)
    
    # 查看现有用户
    view_users()
    
    print("\n" + "=" * 50)
    
    # 创建管理员账号
    create_admin_user()
    
    print("\n" + "=" * 50)
    
    # 再次查看用户列表确认
    view_users()
    
    print("\n🎉 管理员账号信息:")
    print("   邮箱: admin@diyassistant.com")
    print("   密码: DIYAdmin2025!")
    print("   类型: 管理员")
    
    print(f"\n💾 数据库备份: {BACKUP_PATH}")

if __name__ == "__main__":
    main()