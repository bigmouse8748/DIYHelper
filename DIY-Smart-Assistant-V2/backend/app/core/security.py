"""
Security Module - Password hashing and verification
"""

import bcrypt
import secrets
from typing import Optional


class PasswordService:
    """Service for password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)


class SecurityService:
    """General security utilities"""
    
    @staticmethod
    def generate_secret_key() -> str:
        """Generate a secret key for JWT signing"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """Generate a numeric verification code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])