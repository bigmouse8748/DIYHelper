"""
User service for database operations
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.user_models import User, MembershipLevel
from database import get_db_session
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service for user database operations"""
    
    @staticmethod
    def create_user(email: str, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Create a new user and return user data"""
        try:
            with get_db_session() as db:
                # Check if user already exists
                existing_user = db.query(User).filter(
                    (User.email == email) | (User.username == username)
                ).first()
                
                if existing_user:
                    logger.warning(f"User creation failed: email or username already exists")
                    return None
                
                # Create new user
                new_user = User(
                    email=email,
                    username=username,
                    password_hash=User.hash_password(password),
                    membership_level=MembershipLevel.FREE,
                    created_at=datetime.utcnow(),
                    daily_identifications=0,
                    last_reset=datetime.utcnow()
                )
                
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                
                # Return user data as dict to avoid session issues
                user_data = {
                    "id": new_user.id,
                    "email": new_user.email,
                    "username": new_user.username,
                    "membership_level": new_user.membership_level.value,  # Convert enum to string
                    "created_at": new_user.created_at,
                    "daily_identifications": new_user.daily_identifications
                }
                
                logger.info(f"User created successfully: {username}")
                return user_data
                
        except IntegrityError as e:
            logger.error(f"User creation failed due to integrity constraint: {e}")
            return None
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.username == username).first()
                return user
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.email == email).first()
                return user
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                return user
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password"""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.username == username).first()
                if user and user.verify_password(password):
                    # Update last login
                    user.last_login = datetime.utcnow()
                    db.commit()
                    
                    # Return user data as dict to avoid session issues
                    user_data = {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "membership_level": user.membership_level,
                        "last_login": user.last_login
                    }
                    
                    logger.info(f"User authenticated successfully: {username}")
                    return user_data
                else:
                    logger.warning(f"Authentication failed for user: {username}")
                    return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    @staticmethod
    def update_last_login(user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user.last_login = datetime.utcnow()
                    db.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False
    
    @staticmethod
    def increment_daily_usage(user_id: int) -> bool:
        """Increment user's daily identification count"""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    # Reset count if it's a new day
                    if user.last_reset and user.last_reset.date() < datetime.utcnow().date():
                        user.daily_identifications = 0
                        user.last_reset = datetime.utcnow()
                    elif user.last_reset is None:
                        # First time user - initialize
                        user.daily_identifications = 0
                        user.last_reset = datetime.utcnow()
                    
                    user.daily_identifications += 1
                    db.commit()
                    logger.info(f"Daily usage incremented for user {user_id}: {user.daily_identifications}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error incrementing daily usage: {e}")
            return False
    
    @staticmethod
    def get_user_quota_info(user_id: int) -> Dict[str, Any]:
        """Get user's quota information"""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    # Reset count if it's a new day
                    if user.last_reset and user.last_reset.date() < datetime.utcnow().date():
                        user.daily_identifications = 0
                        user.last_reset = datetime.utcnow()
                        db.commit()
                    
                    # Get all data within session to avoid session binding issues
                    daily_identifications = user.daily_identifications
                    membership_level = user.membership_level.value
                    
                    # Calculate limits manually to avoid calling methods on detached object
                    limits = {
                        MembershipLevel.FREE: 5,
                        MembershipLevel.PREMIUM: 50,
                        MembershipLevel.PRO: 999999,
                        MembershipLevel.ADMIN: 999999
                    }
                    daily_limit = limits.get(user.membership_level, 5)
                    
                    # Check if can identify
                    can_identify = daily_identifications < daily_limit
                    
                    # Check premium features
                    has_premium = False
                    if user.membership_level in [MembershipLevel.PREMIUM, MembershipLevel.PRO, MembershipLevel.ADMIN]:
                        if user.membership_expiry is None or user.membership_expiry > datetime.utcnow():
                            has_premium = True
                    
                    return {
                        "used": daily_identifications,
                        "limit": daily_limit,
                        "membership": membership_level,
                        "can_identify": can_identify,
                        "has_premium": has_premium
                    }
            return {"used": 0, "limit": 0, "membership": "unknown", "can_identify": False, "has_premium": False}
        except Exception as e:
            logger.error(f"Error getting quota info: {e}")
            return {"used": 0, "limit": 0, "membership": "unknown", "can_identify": False, "has_premium": False}
    
    @staticmethod
    def reset_daily_count(user_id: int) -> bool:
        """Reset daily identification count"""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user.daily_identifications = 0
                    user.last_reset = datetime.utcnow()
                    db.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error resetting daily count: {e}")
            return False
    
    @staticmethod
    def upgrade_membership(user_id: int, level: str, days: int = 30) -> bool:
        """Upgrade user membership"""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user.membership_level = MembershipLevel(level)
                    user.membership_expiry = datetime.utcnow() + timedelta(days=days)
                    db.commit()
                    logger.info(f"Membership upgraded for user {user_id} to {level}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error upgrading membership: {e}")
            return False
    
    @staticmethod
    def user_to_dict(user: User) -> Dict[str, Any]:
        """Convert user object to dictionary"""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "membership_level": user.membership_level.value,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "daily_identifications": user.daily_identifications,
            "daily_limit": user.get_daily_limit(),
            "can_identify": user.can_identify(),
            "has_premium": user.has_premium_features()
        }