#!/usr/bin/env python3
"""
Admin account creation script
"""

import sqlite3
import bcrypt
import secrets
from datetime import datetime
import shutil
import os

# Database path
DB_PATH = "diy_assistant.db"

def create_backup():
    """Create database backup"""
    if os.path.exists(DB_PATH):
        backup_path = f"diy_assistant_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(DB_PATH, backup_path)
        print(f"Database backup created: {backup_path}")
        return backup_path
    else:
        print("Database file not found")
        return None

def view_users():
    """View all users"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, user_type, is_active, created_at 
            FROM users 
            ORDER BY id
        """)
        
        users = cursor.fetchall()
        
        print("\nCurrent users:")
        print("-" * 80)
        print(f"{'ID':<3} {'Username':<15} {'Email':<25} {'Type':<10} {'Active':<6} {'Created':<20}")
        print("-" * 80)
        
        for user in users:
            user_id, username, email, user_type, is_active, created_at = user
            is_active_str = "Yes" if is_active else "No"
            created_str = created_at[:19] if created_at else ""
            
            print(f"{user_id:<3} {username:<15} {email:<25} {user_type:<10} {is_active_str:<6} {created_str:<20}")
        
        print(f"\nTotal: {len(users)} users")
        conn.close()
        
    except Exception as e:
        print(f"Error viewing users: {e}")

def create_admin_user():
    """Create admin account"""
    admin_email = "admin@diyassistant.com"
    admin_username = "admin"
    admin_password = "DIYAdmin2025!"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if admin already exists
        cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (admin_email, admin_username))
        existing = cursor.fetchone()
        
        if existing:
            print(f"Admin account already exists (ID: {existing[0]})")
            return
        
        # Create password hash
        password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Generate email verification token
        email_verify_token = secrets.token_urlsafe(32)
        
        # Insert admin user
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
        
        print(f"Admin account created successfully!")
        print(f"   ID: {admin_id}")
        print(f"   Username: {admin_username}")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"   Type: ADMIN")
        
        conn.close()
        
    except Exception as e:
        print(f"Error creating admin account: {e}")

def view_database_info():
    """View database information"""
    try:
        if os.path.exists(DB_PATH):
            file_size = os.path.getsize(DB_PATH)
            file_time = datetime.fromtimestamp(os.path.getmtime(DB_PATH))
            print(f"Database file: {DB_PATH}")
            print(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print(f"Modified: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("Database file not found")
            return
        
        # Database table info
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\nDatabase tables ({len(tables)}):")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   {table_name}: {count} records")
        
        conn.close()
        
    except Exception as e:
        print(f"Error viewing database info: {e}")

def main():
    """Main function"""
    print("DIY Smart Assistant Database Management Tool")
    print("=" * 50)
    
    # View database info
    view_database_info()
    
    print("\n" + "=" * 50)
    
    # Create backup
    backup_path = create_backup()
    
    print("\n" + "=" * 50)
    
    # View existing users
    view_users()
    
    print("\n" + "=" * 50)
    
    # Create admin account
    create_admin_user()
    
    print("\n" + "=" * 50)
    
    # View users again to confirm
    view_users()
    
    print("\nAdmin Account Information:")
    print("   Email: admin@diyassistant.com")
    print("   Password: DIYAdmin2025!")
    print("   Type: Administrator")
    
    if backup_path:
        print(f"\nDatabase backup: {backup_path}")

if __name__ == "__main__":
    main()