#!/usr/bin/env python3
"""
Script to update admin user type
"""

import asyncio
import sqlite3
import os

def update_admin_user():
    """Update admin user to have admin privileges"""
    
    # Database file path
    db_path = "diy_assistant.db"
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current admin user
        cursor.execute("SELECT id, email, user_type FROM users WHERE email = ?", ('admin@diyassistant.com',))
        user = cursor.fetchone()
        
        if user:
            user_id, email, current_type = user
            print(f"Found user: {email} (ID: {user_id}, Type: {current_type})")
            
            # Update user type to admin if not already
            if current_type != 'admin':
                cursor.execute("UPDATE users SET user_type = ? WHERE id = ?", ('admin', user_id))
                conn.commit()
                print(f"Updated user {email} to admin type")
            else:
                print(f"User {email} is already admin")
        else:
            print("Admin user not found")
        
        # List all users for verification
        print("\nAll users:")
        cursor.execute("SELECT id, email, username, user_type FROM users")
        users = cursor.fetchall()
        for user in users:
            print(f"  ID: {user[0]}, Email: {user[1]}, Username: {user[2]}, Type: {user[3]}")
        
        conn.close()
        print("\nAdmin user update completed successfully!")
        
    except Exception as e:
        print(f"Error updating admin user: {e}")


if __name__ == "__main__":
    update_admin_user()