"""
Enhanced DIY Agent System with Tool Identification and User Management
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import base64

# Import core modules
from core import agent_manager
from utils.config import get_settings
from agents.product_recommendation_agent import ProductRecommendationAgent
from agents.tool_identification_agent import ToolIdentificationAgent
from auth.auth_handler import (
    create_access_token, 
    get_current_user,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="DIY Agent System Enhanced",
    description="智能DIY项目分析、工具识别和购物助手",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
tool_identification_agent = ToolIdentificationAgent()

# Data models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_info: Dict[str, Any]

class ToolIdentificationRequest(BaseModel):
    include_alternatives: bool = True
    max_results: int = 5

class ToolIdentificationResponse(BaseModel):
    tool_info: Dict[str, Any]
    exact_matches: List[Dict[str, Any]]
    alternatives: List[Dict[str, Any]]
    search_timestamp: str
    user_quota: Dict[str, Any]

# Mock user database (would be replaced with real database)
mock_users_db = {}
user_identifications = {}  # Track daily usage

# User management endpoints
@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """Register a new user"""
    try:
        # Check if user exists
        if user.username in mock_users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Create user
        hashed_password = get_password_hash(user.password)
        mock_users_db[user.username] = {
            "email": user.email,
            "username": user.username,
            "password_hash": hashed_password,
            "membership_level": "free",
            "created_at": datetime.utcnow().isoformat(),
            "daily_identifications": 0,
            "last_reset": datetime.utcnow().date().isoformat()
        }
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.username, "email": user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_info={
                "username": user.username,
                "email": user.email,
                "membership_level": "free"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """User login"""
    try:
        # Verify user
        user = mock_users_db.get(form_data.username)
        if not user or not verify_password(form_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user["username"], "email": user["email"]},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_info={
                "username": user["username"],
                "email": user["email"],
                "membership_level": user.get("membership_level", "free")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    username = current_user.get("user_id")
    user = mock_users_db.get(username)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "username": user["username"],
        "email": user["email"],
        "membership_level": user.get("membership_level", "free"),
        "daily_identifications": user.get("daily_identifications", 0),
        "daily_limit": get_daily_limit(user.get("membership_level", "free"))
    }

# Tool identification endpoints
@app.post("/api/identify-tool", response_model=ToolIdentificationResponse)
async def identify_tool(
    image: UploadFile = File(...),
    include_alternatives: bool = Form(default=True),
    current_user: dict = Depends(get_current_user)
):
    """Identify tool from uploaded image"""
    try:
        username = current_user.get("user_id")
        user = mock_users_db.get(username)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check daily quota
        membership = user.get("membership_level", "free")
        daily_limit = get_daily_limit(membership)
        daily_count = check_and_update_daily_usage(username)
        
        if daily_count >= daily_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily limit ({daily_limit}) reached. Upgrade to premium for more."
            )
        
        # Read and encode image
        image_content = await image.read()
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Create agent task
        from core.agent_base import AgentTask
        task = AgentTask(
            task_id=f"tool_id_{username}_{datetime.utcnow().timestamp()}",
            agent_name="tool_identification",
            input_data={
                "image_data": image_base64,
                "include_alternatives": include_alternatives,
                "membership_level": membership
            },
            created_at=datetime.utcnow()
        )
        
        # Process identification
        result = await tool_identification_agent.process_task(task)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        # Save to history (mock implementation)
        save_identification_history(username, result.data)
        
        # Update usage count
        increment_daily_usage(username)
        
        # Prepare response
        response_data = result.data
        response_data["user_quota"] = {
            "used": daily_count + 1,
            "limit": daily_limit,
            "membership": membership
        }
        
        return ToolIdentificationResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool identification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Identification failed")

@app.get("/api/identification-history")
async def get_identification_history(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get user's identification history"""
    username = current_user.get("user_id")
    history = user_identifications.get(username, [])
    
    # Filter based on membership (free users only see last 7 days)
    user = mock_users_db.get(username)
    membership = user.get("membership_level", "free") if user else "free"
    
    if membership == "free":
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        history = [h for h in history if datetime.fromisoformat(h["timestamp"]) > cutoff_date]
    
    return {
        "history": history[:limit],
        "total": len(history),
        "membership": membership
    }

@app.delete("/api/identification-history/{identification_id}")
async def delete_identification(
    identification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete identification from history"""
    username = current_user.get("user_id")
    
    if username in user_identifications:
        user_identifications[username] = [
            h for h in user_identifications[username] 
            if h.get("id") != identification_id
        ]
    
    return {"success": True, "message": "Identification deleted"}

# Membership endpoints
@app.post("/api/membership/upgrade")
async def upgrade_membership(
    level: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Upgrade user membership"""
    username = current_user.get("user_id")
    user = mock_users_db.get(username)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if level not in ["premium", "pro"]:
        raise HTTPException(status_code=400, detail="Invalid membership level")
    
    # Mock payment processing
    user["membership_level"] = level
    user["membership_expiry"] = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    return {
        "success": True,
        "membership": level,
        "expiry": user["membership_expiry"]
    }

# Original DIY analysis endpoint (kept for compatibility)
@app.post("/analyze-project")
async def analyze_project(
    images: List[UploadFile] = File(...),
    description: str = Form(default=""),
    project_type: str = Form(default=""),
    budget_range: str = Form(default="")
):
    """Original DIY project analysis endpoint"""
    # Implementation from main_simple.py
    # ... (keep existing implementation)
    return {"success": True, "message": "See main_simple.py for full implementation"}

# Helper functions
def get_daily_limit(membership: str) -> int:
    """Get daily identification limit by membership"""
    limits = {
        "free": 5,
        "premium": 50,
        "pro": 999999
    }
    return limits.get(membership, 5)

def check_and_update_daily_usage(username: str) -> int:
    """Check and reset daily usage if needed"""
    user = mock_users_db.get(username, {})
    last_reset = user.get("last_reset", datetime.utcnow().date().isoformat())
    
    # Reset if new day
    if last_reset != datetime.utcnow().date().isoformat():
        user["daily_identifications"] = 0
        user["last_reset"] = datetime.utcnow().date().isoformat()
        mock_users_db[username] = user
    
    return user.get("daily_identifications", 0)

def increment_daily_usage(username: str):
    """Increment daily usage count"""
    if username in mock_users_db:
        mock_users_db[username]["daily_identifications"] = \
            mock_users_db[username].get("daily_identifications", 0) + 1

def save_identification_history(username: str, data: dict):
    """Save identification to history"""
    if username not in user_identifications:
        user_identifications[username] = []
    
    history_entry = {
        "id": f"id_{datetime.utcnow().timestamp()}",
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }
    
    user_identifications[username].insert(0, history_entry)

# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DIY Agent System Enhanced API",
        "version": "2.0.0",
        "features": ["diy_analysis", "tool_identification", "user_management"],
        "status": "running"
    }

@app.get("/api/test")
async def test_api():
    """API test endpoint"""
    return {
        "message": "API connection successful",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Enhanced DIY Agent System...")
    logger.info("Features: Tool Identification, User Management, Membership System")
    
    # Create test user for demo
    if "demo" not in mock_users_db:
        mock_users_db["demo"] = {
            "email": "demo@example.com",
            "username": "demo",
            "password_hash": get_password_hash("demo123"),
            "membership_level": "premium",
            "created_at": datetime.utcnow().isoformat(),
            "daily_identifications": 0,
            "last_reset": datetime.utcnow().date().isoformat()
        }
        logger.info("Demo user created - username: demo, password: demo123")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Enhanced DIY Agent System...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )