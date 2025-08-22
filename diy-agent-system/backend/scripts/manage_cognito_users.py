#!/usr/bin/env python3
"""
Script to manage Cognito users
- List all users
- Delete all users except admin
- Create admin user
"""

import os
import sys
import boto3
import logging
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cognito Configuration
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")

def list_all_users():
    """List all users in the Cognito User Pool"""
    
    if not COGNITO_USER_POOL_ID:
        logger.error("COGNITO_USER_POOL_ID not found in environment variables")
        return []
    
    cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
    
    try:
        all_users = []
        next_token = None
        
        while True:
            if next_token:
                response = cognito_client.list_users(
                    UserPoolId=COGNITO_USER_POOL_ID,
                    Limit=60,
                    PaginationToken=next_token
                )
            else:
                response = cognito_client.list_users(
                    UserPoolId=COGNITO_USER_POOL_ID,
                    Limit=60
                )
            
            users = response.get('Users', [])
            all_users.extend(users)
            
            next_token = response.get('PaginationToken')
            if not next_token:
                break
        
        logger.info(f"Found {len(all_users)} total users:")
        for i, user in enumerate(all_users, 1):
            username = user['Username']
            email = 'N/A'
            status = user.get('UserStatus', 'Unknown')
            created = user.get('UserCreateDate', 'Unknown')
            
            # Get email from attributes
            for attr in user.get('Attributes', []):
                if attr['Name'] == 'email':
                    email = attr['Value']
                    break
            
            # Get user groups
            try:
                groups_response = cognito_client.admin_list_groups_for_user(
                    Username=username,
                    UserPoolId=COGNITO_USER_POOL_ID
                )
                groups = [g['GroupName'] for g in groups_response.get('Groups', [])]
            except:
                groups = []
            
            logger.info(f"  {i}. {username}")
            logger.info(f"     Email: {email}")
            logger.info(f"     Status: {status}")
            logger.info(f"     Groups: {groups}")
            logger.info(f"     Created: {created}")
            logger.info("")
        
        return all_users
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        return []

def delete_user(username):
    """Delete a specific user"""
    
    cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
    
    try:
        cognito_client.admin_delete_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username
        )
        logger.info(f"✅ Deleted user: {username}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to delete user {username}: {str(e)}")
        return False

def delete_all_users_except_admin():
    """Delete all users except those in admin group"""
    
    users = list_all_users()
    
    if not users:
        logger.info("No users found to delete")
        return
    
    # Find admin users
    admin_users = []
    regular_users = []
    
    cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
    
    for user in users:
        username = user['Username']
        try:
            groups_response = cognito_client.admin_list_groups_for_user(
                Username=username,
                UserPoolId=COGNITO_USER_POOL_ID
            )
            groups = [g['GroupName'] for g in groups_response.get('Groups', [])]
            
            if 'admin' in groups or 'admins' in groups:
                admin_users.append(username)
            else:
                regular_users.append(username)
                
        except Exception as e:
            logger.warning(f"Could not get groups for {username}: {str(e)}")
            regular_users.append(username)  # Assume non-admin if can't check
    
    logger.info(f"Found {len(admin_users)} admin users: {admin_users}")
    logger.info(f"Found {len(regular_users)} regular users to delete: {regular_users}")
    
    if not regular_users:
        logger.info("No regular users to delete")
        return
    
    # Confirm deletion
    print(f"\nWARNING: This will delete {len(regular_users)} users!")
    print("Users to be deleted:")
    for username in regular_users:
        print(f"  - {username}")
    
    print(f"\nUsers to be KEPT (admins):")
    for username in admin_users:
        print(f"  - {username}")
    
    confirmation = input(f"\nType 'DELETE {len(regular_users)} USERS' to confirm: ")
    
    if confirmation != f"DELETE {len(regular_users)} USERS":
        logger.info("Operation cancelled")
        return
    
    # Delete users
    deleted_count = 0
    for username in regular_users:
        if delete_user(username):
            deleted_count += 1
    
    logger.info(f"✅ Successfully deleted {deleted_count}/{len(regular_users)} users")

def create_admin_user(email, password, username):
    """Create a new admin user"""
    
    cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
    
    try:
        # Create user - use username as identifier, email as attribute
        response = cognito_client.admin_create_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,  # Use username instead of email
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'},
                {'Name': 'preferred_username', 'Value': username}
            ],
            TemporaryPassword=password,
            MessageAction='SUPPRESS'  # Don't send welcome email
        )
        
        # Set permanent password
        cognito_client.admin_set_user_password(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,  # Use username instead of email
            Password=password,
            Permanent=True
        )
        
        # Add to admin group
        cognito_client.admin_add_user_to_group(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,  # Use username instead of email
            GroupName='admin'
        )
        
        logger.info(f"✅ Created admin user: {email} ({username})")
        logger.info(f"   Password: {password}")
        logger.info(f"   Added to 'admin' group")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create admin user: {str(e)}")
        return False

def main():
    if not COGNITO_USER_POOL_ID:
        logger.error("COGNITO_USER_POOL_ID not found in environment variables")
        return
    
    logger.info("=== Cognito User Management ===")
    logger.info(f"User Pool ID: {COGNITO_USER_POOL_ID}")
    logger.info(f"Region: {COGNITO_REGION}")
    logger.info("")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            list_all_users()
            
        elif command == "clean":
            logger.info("Cleaning users (keeping only admins)...")
            delete_all_users_except_admin()
            
        elif command == "create-admin":
            if len(sys.argv) < 5:
                logger.error("Usage: python manage_cognito_users.py create-admin <email> <password> <username>")
                return
            
            email = sys.argv[2]
            password = sys.argv[3]
            username = sys.argv[4]
            
            create_admin_user(email, password, username)
            
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands:")
            logger.info("  list - List all users")
            logger.info("  clean - Delete all non-admin users")
            logger.info("  create-admin <email> <password> <username> - Create admin user")
    else:
        logger.info("Available commands:")
        logger.info("  list - List all users")
        logger.info("  clean - Delete all non-admin users")
        logger.info("  create-admin <email> <password> <username> - Create admin user")
        logger.info("")
        logger.info("Example:")
        logger.info("  python manage_cognito_users.py list")
        logger.info("  python manage_cognito_users.py clean")
        logger.info("  python manage_cognito_users.py create-admin admin@example.com AdminPass123 admin")

if __name__ == "__main__":
    main()