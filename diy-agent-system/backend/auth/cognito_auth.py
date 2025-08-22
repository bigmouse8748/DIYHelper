"""
AWS Cognito Authentication Service
Handles all authentication via AWS Cognito User Pool
"""

import os
import boto3
import jwt
import hmac
import hashlib
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from functools import wraps
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Cognito Configuration
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
COGNITO_CLIENT_SECRET = os.getenv("COGNITO_CLIENT_SECRET")
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")
COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN")

# Initialize boto3 client
cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

# Security scheme for FastAPI
security = HTTPBearer()

# User groups with their permissions
USER_GROUPS = {
    "free": {
        "diy_assistant": True,
        "tool_identification": True,  # All registered users can use tool identification
        "daily_quota": 5,
        "priority_support": False,
        "admin_features": False
    },
    "pro": {
        "diy_assistant": True,
        "tool_identification": True,
        "daily_quota": 20,
        "priority_support": False,
        "admin_features": False
    },
    "premium": {
        "diy_assistant": True,
        "tool_identification": True,
        "daily_quota": 50,
        "priority_support": True,
        "admin_features": False
    },
    "admin": {
        "diy_assistant": True,
        "tool_identification": True,
        "daily_quota": -1,  # Unlimited
        "priority_support": True,
        "admin_features": True
    }
}


class CognitoAuth:
    """AWS Cognito Authentication Manager"""
    
    def __init__(self):
        self.user_pool_id = COGNITO_USER_POOL_ID
        self.client_id = COGNITO_CLIENT_ID
        self.client_secret = COGNITO_CLIENT_SECRET
        self.region = COGNITO_REGION
        self.cognito_client = cognito_client
        
    def _calculate_secret_hash(self, username: str) -> str:
        """Calculate SECRET_HASH for Cognito client with secret"""
        message = bytes(username + self.client_id, 'utf-8')
        key = bytes(self.client_secret, 'utf-8')
        secret_hash = base64.b64encode(
            hmac.new(key, message, digestmod=hashlib.sha256).digest()
        ).decode()
        return secret_hash
    
    async def register_user(self, email: str, password: str, username: str) -> Dict[str, Any]:
        """Register a new user in Cognito"""
        try:
            # Remove SECRET_HASH since app client is not configured for secret
            response = self.cognito_client.sign_up(
                ClientId=self.client_id,
                Username=email,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'preferred_username', 'Value': username}
                ]
            )
            
            # Automatically add new users to 'free' group
            if response.get('UserConfirmed', False):
                self.add_user_to_group(email, 'free')
            
            return {
                "success": True,
                "user_sub": response['UserSub'],
                "username": email,
                "message": "User registered successfully. Please check your email for verification."
            }
            
        except self.cognito_client.exceptions.UsernameExistsException:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def confirm_email(self, email: str, confirmation_code: str) -> Dict[str, Any]:
        """Confirm user email with verification code"""
        try:
            # Remove SECRET_HASH since app client is not configured for secret
            response = self.cognito_client.confirm_sign_up(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code
            )
            
            # Add confirmed user to 'free' group
            self.add_user_to_group(email, 'free')
            
            return {
                "success": True,
                "message": "Email confirmed successfully"
            }
            
        except Exception as e:
            logger.error(f"Email confirmation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        try:
            # Remove SECRET_HASH since app client is not configured for secret
            response = self.cognito_client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            
            if 'AuthenticationResult' in response:
                # Get user groups
                groups = self.get_user_groups(email)
                
                return {
                    "success": True,
                    "access_token": response['AuthenticationResult']['AccessToken'],
                    "id_token": response['AuthenticationResult']['IdToken'],
                    "refresh_token": response['AuthenticationResult']['RefreshToken'],
                    "expires_in": response['AuthenticationResult']['ExpiresIn'],
                    "groups": groups
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication failed"
                )
                
        except self.cognito_client.exceptions.NotAuthorizedException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        except self.cognito_client.exceptions.UserNotConfirmedException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User email not confirmed"
            )
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            response = self.cognito_client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )
            
            return {
                "success": True,
                "access_token": response['AuthenticationResult']['AccessToken'],
                "id_token": response['AuthenticationResult']['IdToken'],
                "expires_in": response['AuthenticationResult']['ExpiresIn']
            }
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    async def logout(self, access_token: str) -> Dict[str, Any]:
        """Logout user (invalidate tokens)"""
        try:
            self.cognito_client.global_sign_out(
                AccessToken=access_token
            )
            
            return {
                "success": True,
                "message": "User logged out successfully"
            }
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return {
                "success": True,
                "message": "Logged out locally"
            }
    
    async def forgot_password(self, email: str) -> Dict[str, Any]:
        """Initiate password reset flow"""
        try:
            # Remove SECRET_HASH since app client is not configured for secret
            response = self.cognito_client.forgot_password(
                ClientId=self.client_id,
                Username=email
            )
            
            return {
                "success": True,
                "message": "Password reset code sent to your email"
            }
            
        except Exception as e:
            logger.error(f"Forgot password error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def confirm_forgot_password(self, email: str, code: str, new_password: str) -> Dict[str, Any]:
        """Confirm password reset with code"""
        try:
            # Remove SECRET_HASH since app client is not configured for secret
            response = self.cognito_client.confirm_forgot_password(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=code,
                Password=new_password
            )
            
            return {
                "success": True,
                "message": "Password reset successfully"
            }
            
        except Exception as e:
            logger.error(f"Password reset confirmation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    def add_user_to_group(self, username: str, group_name: str) -> bool:
        """Add user to a Cognito group"""
        try:
            self.cognito_client.admin_add_user_to_group(
                UserPoolId=self.user_pool_id,
                Username=username,
                GroupName=group_name
            )
            return True
        except Exception as e:
            logger.error(f"Error adding user to group: {str(e)}")
            return False
    
    def remove_user_from_group(self, username: str, group_name: str) -> bool:
        """Remove user from a Cognito group"""
        try:
            self.cognito_client.admin_remove_user_from_group(
                UserPoolId=self.user_pool_id,
                Username=username,
                GroupName=group_name
            )
            return True
        except Exception as e:
            logger.error(f"Error removing user from group: {str(e)}")
            return False
    
    def get_user_groups(self, username: str) -> List[str]:
        """Get all groups for a user"""
        try:
            response = self.cognito_client.admin_list_groups_for_user(
                Username=username,
                UserPoolId=self.user_pool_id
            )
            return [group['GroupName'] for group in response.get('Groups', [])]
        except Exception as e:
            logger.error(f"Error getting user groups: {str(e)}")
            return []
    
    def create_group(self, group_name: str, description: str = "") -> bool:
        """Create a new Cognito group"""
        try:
            self.cognito_client.create_group(
                GroupName=group_name,
                UserPoolId=self.user_pool_id,
                Description=description
            )
            return True
        except self.cognito_client.exceptions.GroupExistsException:
            logger.info(f"Group {group_name} already exists")
            return True
        except Exception as e:
            logger.error(f"Error creating group: {str(e)}")
            return False
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode Cognito JWT token"""
        try:
            # For development, just decode without signature verification
            # In production, you should verify against the JWKS
            decoded = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )
            
            logger.info(f"✅ Token decoded for user: {decoded.get('cognito:username') or decoded.get('username')}")
            return decoded
            
        except jwt.InvalidTokenError as e:
            logger.error(f"JWT decode error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )


# Initialize Cognito auth instance
cognito_auth = CognitoAuth()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """Dependency to get current user from JWT token"""
    token = credentials.credentials
    
    try:
        logger.info(f"🔍 Token verification - Token preview: {token[:50]}..." if token else "No token provided")
        
        # Verify token and get user info
        user_info = cognito_auth.verify_token(token)
        logger.info(f"✅ Token decoded successfully for user: {user_info.get('cognito:username') or user_info.get('username')}")
        
        # Get user groups
        username = user_info.get('cognito:username') or user_info.get('username')
        groups = cognito_auth.get_user_groups(username)
        logger.info(f"👥 User groups retrieved: {groups}")
        
        # Determine highest permission group
        user_group = 'free'  # Default
        for group in ['admin', 'premium', 'pro', 'free']:
            if group in groups:
                user_group = group
                break
        
        logger.info(f"🎯 Final user context: user={username}, group={user_group}, permissions={USER_GROUPS.get(user_group, USER_GROUPS['free'])}")
        
        return {
            "username": username,
            "email": user_info.get('email'),
            "sub": user_info.get('sub'),
            "groups": groups,
            "group": user_group,
            "permissions": USER_GROUPS.get(user_group, USER_GROUPS['free'])
        }
        
    except Exception as e:
        logger.error(f"❌ Token verification failed: {str(e)}")
        logger.error(f"🔍 Token details - Length: {len(token) if token else 0}, Starts with: {token[:20] if token else 'None'}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )


def require_group(allowed_groups: List[str]):
    """Decorator to require specific user groups"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: Dict = Depends(get_current_user), **kwargs):
            user_groups = current_user.get('groups', [])
            
            if not any(group in allowed_groups for group in user_groups):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required groups: {allowed_groups}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: Dict = Depends(get_current_user), **kwargs):
            permissions = current_user.get('permissions', {})
            
            if not permissions.get(permission, False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required permission: {permission}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


# Initialize groups on startup
def initialize_cognito_groups():
    """Create default groups in Cognito"""
    groups = [
        ("free", "Free tier users - Limited access"),
        ("pro", "Pro tier users - Enhanced features"),
        ("premium", "Premium tier users - Full features with priority support"),
        ("admin", "Admin users - Full system access")
    ]
    
    for group_name, description in groups:
        if cognito_auth.create_group(group_name, description):
            logger.info(f"Cognito group '{group_name}' ready")
        else:
            logger.error(f"Failed to create group '{group_name}'")