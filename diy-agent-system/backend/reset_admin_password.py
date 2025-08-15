"""
Reset admin password utility
"""
import sys
import bcrypt
import sqlite3

def reset_admin_password(new_password: str):
    """Reset the admin user's password"""
    try:
        # Hash the new password using bcrypt directly
        password_bytes = new_password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        # Connect to database
        conn = sqlite3.connect('local_test.db')
        cursor = conn.cursor()
        
        # Update admin password
        cursor.execute("""
            UPDATE users 
            SET password_hash = ? 
            WHERE username = 'admin' AND membership_level = 'ADMIN'
        """, (hashed_password,))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected > 0:
            print("SUCCESS: Admin password reset!")
            print(f"Username: admin")
            print(f"New Password: {new_password}")
            print(f"\nYou can now login at: http://localhost:3002/login")
        else:
            print("ERROR: No admin user found to update")
            
    except Exception as e:
        print(f"ERROR: Failed to reset password: {e}")

if __name__ == "__main__":
    # Set a new password
    new_password = "Admin123!"
    
    print("Resetting admin password...")
    reset_admin_password(new_password)