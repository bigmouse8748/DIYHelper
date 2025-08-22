#!/usr/bin/env python3
"""
Script to set up Cognito User Groups
Creates free, pro, premium, and admin groups in AWS Cognito User Pool
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

def setup_cognito_groups():
    """Create user groups in Cognito User Pool"""
    
    if not COGNITO_USER_POOL_ID:
        logger.error("COGNITO_USER_POOL_ID not found in environment variables")
        return False
    
    # Initialize boto3 client
    cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
    
    # Define groups with descriptions
    groups = [
        {
            "GroupName": "free",
            "Description": "Free tier users - Limited access to basic features (5 daily requests)",
            "Precedence": 40  # Lower precedence = higher priority
        },
        {
            "GroupName": "pro", 
            "Description": "Pro tier users - Enhanced features including tool identification (20 daily requests)",
            "Precedence": 30
        },
        {
            "GroupName": "premium",
            "Description": "Premium tier users - Full features with priority support (50 daily requests)",
            "Precedence": 20
        },
        {
            "GroupName": "admin",
            "Description": "Admin users - Full system access with unlimited requests",
            "Precedence": 10  # Highest priority
        }
    ]
    
    success_count = 0
    
    for group in groups:
        try:
            response = cognito_client.create_group(
                UserPoolId=COGNITO_USER_POOL_ID,
                GroupName=group["GroupName"],
                Description=group["Description"],
                Precedence=group["Precedence"]
            )
            
            logger.info(f"✅ Created group: {group['GroupName']} - {group['Description']}")
            success_count += 1
            
        except cognito_client.exceptions.GroupExistsException:
            logger.info(f"ℹ️  Group '{group['GroupName']}' already exists")
            success_count += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to create group '{group['GroupName']}': {str(e)}")
    
    logger.info(f"Group setup complete: {success_count}/{len(groups)} groups ready")
    return success_count == len(groups)

def list_existing_groups():
    """List all existing groups in the User Pool"""
    
    if not COGNITO_USER_POOL_ID:
        logger.error("COGNITO_USER_POOL_ID not found in environment variables")
        return
    
    cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
    
    try:
        response = cognito_client.list_groups(UserPoolId=COGNITO_USER_POOL_ID)
        
        groups = response.get('Groups', [])
        
        if groups:
            logger.info(f"Found {len(groups)} existing groups:")
            for group in groups:
                logger.info(f"  • {group['GroupName']} (Precedence: {group.get('Precedence', 'N/A')})")
                logger.info(f"    Description: {group.get('Description', 'No description')}")
                logger.info(f"    Created: {group.get('CreationDate', 'Unknown')}")
                logger.info("")
        else:
            logger.info("No existing groups found")
            
    except Exception as e:
        logger.error(f"Failed to list groups: {str(e)}")

def delete_all_groups():
    """Delete all groups (use with caution!)"""
    
    if not COGNITO_USER_POOL_ID:
        logger.error("COGNITO_USER_POOL_ID not found in environment variables")
        return
    
    confirmation = input("⚠️  Are you sure you want to delete ALL groups? This cannot be undone. Type 'DELETE' to confirm: ")
    
    if confirmation != "DELETE":
        logger.info("Operation cancelled")
        return
    
    cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
    
    try:
        response = cognito_client.list_groups(UserPoolId=COGNITO_USER_POOL_ID)
        groups = response.get('Groups', [])
        
        for group in groups:
            try:
                cognito_client.delete_group(
                    UserPoolId=COGNITO_USER_POOL_ID,
                    GroupName=group['GroupName']
                )
                logger.info(f"🗑️  Deleted group: {group['GroupName']}")
            except Exception as e:
                logger.error(f"Failed to delete group '{group['GroupName']}': {str(e)}")
                
    except Exception as e:
        logger.error(f"Failed to list groups for deletion: {str(e)}")

if __name__ == "__main__":
    logger.info("=== AWS Cognito User Groups Setup ===")
    logger.info(f"User Pool ID: {COGNITO_USER_POOL_ID}")
    logger.info(f"Region: {COGNITO_REGION}")
    logger.info("")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            logger.info("Listing existing groups...")
            list_existing_groups()
            
        elif command == "delete":
            logger.info("Deleting all groups...")
            delete_all_groups()
            
        elif command == "setup":
            logger.info("Setting up user groups...")
            if setup_cognito_groups():
                logger.info("✅ All groups set up successfully!")
            else:
                logger.error("❌ Some groups failed to set up")
                
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands: setup, list, delete")
    else:
        # Default action: setup groups
        logger.info("Setting up user groups...")
        if setup_cognito_groups():
            logger.info("✅ All groups set up successfully!")
            logger.info("")
            logger.info("📋 Group Permissions Summary:")
            logger.info("  • free: DIY Assistant only (5 daily requests)")
            logger.info("  • pro: + Tool Identification (20 daily requests)")
            logger.info("  • premium: + Priority Support (50 daily requests)")
            logger.info("  • admin: + Admin Features (unlimited requests)")
        else:
            logger.error("❌ Some groups failed to set up")