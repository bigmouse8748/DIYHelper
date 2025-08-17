"""
Add is_active field to existing users table
"""
import os
import sqlite3
from pathlib import Path

# Get database path
db_path = Path(__file__).parent / "diy_assistant.db"

if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if is_active column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'is_active' not in columns:
            # Add is_active column with default value True (1 in SQLite)
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
            
            # Set all existing users to active
            cursor.execute("UPDATE users SET is_active = 1 WHERE is_active IS NULL")
            
            conn.commit()
            print("Successfully added is_active field to users table")
        else:
            print("is_active field already exists in users table")
            
    except Exception as e:
        print(f"Error updating database: {e}")
        conn.rollback()
    finally:
        conn.close()
else:
    print("Database not found. It will be created when the application starts.")