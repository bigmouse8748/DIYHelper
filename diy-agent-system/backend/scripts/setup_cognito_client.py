#!/usr/bin/env python3
"""
Script to create a new Cognito app client without client secret
for frontend (public client) use
"""

import os
import sys
import boto3
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cognito Configuration
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")

def create_frontend_client():
    """Create a new app client for frontend without client secret"""
    
    if not COGNITO_USER_POOL_ID:
        logger.error("COGNITO_USER_POOL_ID not found in environment variables")
        return None
    
    cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
    
    try:
        response = cognito_client.create_user_pool_client(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientName='diy-frontend-client',
            GenerateSecret=False,  # No client secret for frontend
            RefreshTokenValidity=30,  # 30 days
            AccessTokenValidity=1,   # 1 hour
            IdTokenValidity=1,       # 1 hour
            TokenValidityUnits={
                'RefreshToken': 'days',
                'AccessToken': 'hours', 
                'IdToken': 'hours'
            },
            ExplicitAuthFlows=[
                'ALLOW_USER_SRP_AUTH',
                'ALLOW_USER_PASSWORD_AUTH', 
                'ALLOW_REFRESH_TOKEN_AUTH'
            ],
            SupportedIdentityProviders=['COGNITO'],
            PreventUserExistenceErrors='ENABLED',
            EnableTokenRevocation=True
        )
        
        client_id = response['UserPoolClient']['ClientId']
        logger.info(f"✅ Created frontend client: {client_id}")
        logger.info(f"   Client Name: diy-frontend-client")
        logger.info(f"   Generate Secret: False")
        logger.info(f"   Auth Flows: SRP, Password, Refresh Token")
        
        # Update .env with new client ID
        update_env_file(client_id)
        
        return client_id
        
    except Exception as e:
        logger.error(f"❌ Failed to create frontend client: {str(e)}")
        return None

def update_env_file(new_client_id):
    """Update .env file with new client ID"""
    
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    
    try:
        # Read current .env content
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the client ID line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('COGNITO_CLIENT_ID='):
                lines[i] = f'COGNITO_CLIENT_ID={new_client_id}'
                break
        
        # Write back to file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"✅ Updated .env file with new client ID: {new_client_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to update .env file: {str(e)}")

def list_existing_clients():
    """List all existing app clients"""
    
    if not COGNITO_USER_POOL_ID:
        logger.error("COGNITO_USER_POOL_ID not found in environment variables")
        return
    
    cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
    
    try:
        response = cognito_client.list_user_pool_clients(
            UserPoolId=COGNITO_USER_POOL_ID,
            MaxResults=60
        )
        
        clients = response.get('UserPoolClients', [])
        
        if clients:
            logger.info(f"Found {len(clients)} existing clients:")
            for client in clients:
                # Get detailed info
                detail_response = cognito_client.describe_user_pool_client(
                    UserPoolId=COGNITO_USER_POOL_ID,
                    ClientId=client['ClientId']
                )
                
                client_detail = detail_response['UserPoolClient']
                has_secret = 'ClientSecret' in client_detail
                
                logger.info(f"  • {client['ClientName']} ({client['ClientId']})")
                logger.info(f"    Has Secret: {has_secret}")
                logger.info(f"    Created: {client.get('CreationDate', 'Unknown')}")
                logger.info("")
        else:
            logger.info("No existing clients found")
            
    except Exception as e:
        logger.error(f"Failed to list clients: {str(e)}")

def delete_client(client_id):
    """Delete a specific app client"""
    
    if not COGNITO_USER_POOL_ID:
        logger.error("COGNITO_USER_POOL_ID not found in environment variables")
        return False
    
    cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)
    
    try:
        cognito_client.delete_user_pool_client(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientId=client_id
        )
        logger.info(f"✅ Deleted client: {client_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to delete client {client_id}: {str(e)}")
        return False

def main():
    if not COGNITO_USER_POOL_ID:
        logger.error("COGNITO_USER_POOL_ID not found in environment variables")
        return
    
    logger.info("=== Cognito App Client Management ===")
    logger.info(f"User Pool ID: {COGNITO_USER_POOL_ID}")
    logger.info(f"Region: {COGNITO_REGION}")
    logger.info("")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            list_existing_clients()
            
        elif command == "create":
            logger.info("Creating frontend client (no secret)...")
            client_id = create_frontend_client()
            if client_id:
                logger.info(f"✅ Frontend client created successfully: {client_id}")
                logger.info("Update your frontend config with this client ID")
            
        elif command == "delete":
            if len(sys.argv) < 3:
                logger.error("Usage: python setup_cognito_client.py delete <client_id>")
                return
            
            client_id = sys.argv[2]
            if delete_client(client_id):
                logger.info(f"✅ Client {client_id} deleted successfully")
                
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands: list, create, delete <client_id>")
    else:
        logger.info("Available commands:")
        logger.info("  list - List all app clients")
        logger.info("  create - Create frontend client (no secret)")
        logger.info("  delete <client_id> - Delete specific client")
        logger.info("")
        logger.info("Example:")
        logger.info("  python setup_cognito_client.py list")
        logger.info("  python setup_cognito_client.py create")

if __name__ == "__main__":
    main()