#!/usr/bin/env python3
"""
Database migration to add project_types column to product_recommendations table
"""
import sqlite3
import json
from pathlib import Path

def migrate_database():
    """Add project_types column to existing database"""
    
    # Use the local test database
    db_path = Path(__file__).parent / "local_test.db"
    
    if not db_path.exists():
        print("Database file not found!")
        return
    
    print(f"Using database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(product_recommendations)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'project_types' not in column_names:
            print("Adding project_types column...")
            
            # Add the project_types column as JSON (TEXT in SQLite)
            cursor.execute("""
                ALTER TABLE product_recommendations 
                ADD COLUMN project_types TEXT DEFAULT '[]'
            """)
            
            # Update existing records to have default empty array
            cursor.execute("""
                UPDATE product_recommendations 
                SET project_types = '[]' 
                WHERE project_types IS NULL
            """)
            
            conn.commit()
            print("Successfully added project_types column!")
            
        else:
            print("project_types column already exists!")
            
        # Show table structure
        cursor.execute("PRAGMA table_info(product_recommendations)")
        columns = cursor.fetchall()
        print(f"\nCurrent table structure ({len(columns)} columns):")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
        # Show count of products
        cursor.execute("SELECT COUNT(*) FROM product_recommendations")
        count = cursor.fetchone()[0]
        print(f"\nTotal products in database: {count}")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()