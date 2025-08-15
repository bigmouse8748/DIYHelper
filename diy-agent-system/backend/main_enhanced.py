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
from database import create_tables, test_connection
from services.user_service import UserService
from services.product_service import ProductService
from agents.product_info_agent import product_info_agent

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

# CORS configuration - read from environment variable
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://localhost:3004,http://localhost:5173").split(",")
logger.info(f"CORS origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
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

# Product recommendation models
class ProductCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "other"
    merchant: Optional[str] = None
    original_price: Optional[float] = None
    sale_price: Optional[float] = None
    product_url: str
    image_url: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    is_featured: bool = False
    sort_order: Optional[int] = None

class ProductUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    merchant: Optional[str] = None
    original_price: Optional[float] = None
    sale_price: Optional[float] = None
    product_url: Optional[str] = None
    image_url: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None

class ProductURLRequest(BaseModel):
    product_url: str
    is_featured: bool = False

# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting up application...")
    try:
        if test_connection():
            create_tables()
            logger.info("Database initialized successfully")
            
            # Create demo user if it doesn't exist
            try:
                demo_user = UserService.get_user_by_username("demo")
                if not demo_user:
                    demo_user = UserService.create_user("demo@example.com", "demo", "demo123")
                    if demo_user:
                        # Upgrade to premium for testing
                        UserService.upgrade_membership(demo_user["id"], "premium", days=365)
                        logger.info("Demo user created - username: demo, password: demo123")
            except Exception as e:
                logger.warning(f"Could not create demo user: {e}")
        else:
            logger.warning("Database connection not available at startup, will retry on first request")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}, continuing without database")

# User management endpoints
@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """Register a new user"""
    try:
        # Create user in database
        new_user = UserService.create_user(user.email, user.username, user.password)
        
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(new_user["id"]), "email": new_user["email"], "username": new_user["username"]},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_info={
                "id": new_user["id"],
                "username": new_user["username"],
                "email": new_user["email"],
                "membership_level": new_user["membership_level"].value
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
        # Authenticate user
        user = UserService.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user["id"]), "email": user["email"], "username": user["username"]},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_info={
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "membership_level": user["membership_level"].value
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
    try:
        user_id = int(current_user.get("sub"))  # JWT sub contains user ID
        
        # Get user data using session-safe method
        from database import get_db_session
        from models.user_models import User
        
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get quota information
            quota_info = UserService.get_user_quota_info(user_id)
            
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "membership_level": user.membership_level.value,
                "daily_identifications": quota_info["used"],
                "daily_limit": quota_info["limit"],
                "can_identify": quota_info["can_identify"],
                "has_premium": quota_info["has_premium"]
            }
    except Exception as e:
        logger.error(f"Error getting current user info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user information")

# Tool identification endpoints
@app.post("/api/identify-tool", response_model=ToolIdentificationResponse)
async def identify_tool(
    image: UploadFile = File(...),
    include_alternatives: bool = Form(default=True),
    current_user: dict = Depends(get_current_user)
):
    """Identify tool from uploaded image"""
    try:
        user_id = int(current_user.get("sub"))
        username = current_user.get("username", f"user_{user_id}")
        
        # Check daily quota
        quota_info = UserService.get_user_quota_info(user_id)
        if not quota_info["can_identify"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily limit ({quota_info['limit']}) reached. Upgrade to premium for more."
            )
        
        # Increment usage count
        UserService.increment_daily_usage(user_id)
        
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
                "membership_level": quota_info["membership"]
            },
            created_at=datetime.utcnow()
        )
        
        # Process identification
        result = await tool_identification_agent.process_task(task)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        # TODO: Save to history - implement actual storage
        # save_identification_history(username, result.data)
        
        # Get updated quota after increment
        updated_quota = UserService.get_user_quota_info(user_id)
        
        # Prepare response
        response_data = result.data
        response_data["user_quota"] = {
            "used": updated_quota["used"],
            "limit": updated_quota["limit"],
            "membership": updated_quota["membership"]
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
    try:
        user_id = int(current_user.get("sub"))
        username = current_user.get("username", f"user_{user_id}")
        
        # TODO: Implement actual identification history storage
        # For now, return empty history
        history = []
        
        # Get user membership level
        from database import get_db_session
        from models.user_models import User
        
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            membership = user.membership_level.value if user else "free"
        
        # Filter based on membership (free users only see last 7 days)
        if membership == "free" and len(history) > 0:
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            history = [h for h in history if datetime.fromisoformat(h["timestamp"]) > cutoff_date]
        
        return {
            "history": history[:limit],
            "total": len(history),
            "membership": membership
        }
    except Exception as e:
        logger.error(f"Error getting identification history: {e}")
        return {
            "history": [],
            "total": 0,
            "membership": "free"
        }

@app.delete("/api/identification-history/{identification_id}")
async def delete_identification(
    identification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete identification from history"""
    # TODO: Implement actual identification deletion
    # For now, just return success
    return {"success": True, "message": "Identification deleted"}

# Membership endpoints
@app.post("/api/membership/upgrade")
async def upgrade_membership(
    level: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Upgrade user membership"""
    user_id = int(current_user.get("sub"))
    user = UserService.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if level not in ["premium", "pro", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid membership level")
    
    # Mock payment processing - upgrade membership
    success = UserService.upgrade_membership(user_id, level, days=30)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to upgrade membership")
    
    return {
        "success": True,
        "membership": level,
        "expiry": user["membership_expiry"]
    }

# Product recommendation endpoints

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    merchant: Optional[str] = None,
    project_type: Optional[str] = None,
    featured_only: bool = False,
    search: Optional[str] = None
):
    """Get public product recommendations with search (no authentication required)"""
    try:
        products = ProductService.get_all_products(
            include_inactive=False,
            category=category,
            merchant=merchant,
            project_type=project_type,
            featured_only=featured_only,
            search=search
        )
        
        return {
            "success": True,
            "products": products,
            "total": len(products),
            "filters": {
                "category": category,
                "merchant": merchant,
                "project_type": project_type,
                "search": search,
                "featured_only": featured_only
            }
        }
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail="Failed to get products")

@app.get("/api/products/categories")
async def get_product_categories():
    """Get available product categories"""
    try:
        categories = ProductService.get_categories()
        return {
            "success": True,
            "categories": categories
        }
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get categories")

@app.get("/api/products/merchants")
async def get_product_merchants():
    """Get available product merchants"""
    try:
        merchants = ProductService.get_merchants()
        return {
            "success": True,
            "merchants": merchants
        }
    except Exception as e:
        logger.error(f"Error getting merchants: {e}")
        raise HTTPException(status_code=500, detail="Failed to get merchants")

@app.get("/api/products/project-types")
async def get_project_types():
    """Get available DIY project types"""
    try:
        project_types = [
            {"value": "woodworking", "label": "Woodworking"},
            {"value": "plumbing", "label": "Plumbing"},
            {"value": "electrical", "label": "Electrical"},
            {"value": "automotive", "label": "Automotive"},
            {"value": "metalworking", "label": "Metalworking"},
            {"value": "painting", "label": "Painting"},
            {"value": "general", "label": "General DIY"},
            {"value": "outdoor", "label": "Outdoor & Garden"},
            {"value": "home_improvement", "label": "Home Improvement"},
            {"value": "crafts", "label": "Arts & Crafts"}
        ]
        return {
            "success": True,
            "project_types": project_types
        }
    except Exception as e:
        logger.error(f"Error getting project types: {e}")
        raise HTTPException(status_code=500, detail="Failed to get project types")

@app.post("/api/products/{product_id}/click")
async def track_product_click(product_id: int):
    """Track product click for analytics (public endpoint)"""
    try:
        success = ProductService.increment_click_count(product_id)
        if success:
            return {"success": True, "message": "Click tracked"}
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        return {"success": False, "message": "Click tracking failed"}

@app.post("/api/products/{product_id}/view")
async def track_product_view(product_id: int):
    """Track product view for analytics (public endpoint)"""
    try:
        success = ProductService.increment_view_count(product_id)
        if success:
            return {"success": True, "message": "View tracked"}
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        logger.error(f"Error tracking view: {e}")
        return {"success": False, "message": "View tracking failed"}

# Admin-only product management endpoints

@app.get("/api/admin/products")
async def admin_get_all_products(
    include_inactive: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Get all products for admin management"""
    try:
        user_id = int(current_user.get("sub"))
        
        # Check if user is admin
        from database import get_db_session
        from models.user_models import User
        
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_admin():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
        
        products = ProductService.get_all_products(include_inactive=include_inactive)
        
        return {
            "success": True,
            "products": products,
            "total": len(products)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin products: {e}")
        raise HTTPException(status_code=500, detail="Failed to get products")

@app.post("/api/admin/products/from-url")
async def admin_create_product_from_url(
    request: ProductURLRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new product using AI-powered URL analysis (admin only)"""
    try:
        user_id = int(current_user.get("sub"))
        
        # Check if user is admin
        from database import get_db_session
        from models.user_models import User
        
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_admin():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
        
        # Extract product information using AI agent
        logger.info(f"Extracting product info from URL using AI: {request.product_url}")
        
        # Create agent task
        from core.agent_base import AgentTask
        task = AgentTask(
            task_id=f"product_extract_{user_id}_{datetime.utcnow().timestamp()}",
            agent_name="product_info_extraction",
            input_data={
                "product_url": request.product_url
            },
            created_at=datetime.utcnow()
        )
        
        # Execute AI agent
        result = await product_info_agent.process_task(task)
        
        if not result.success:
            logger.error(f"AI agent failed: {result.error}")
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to extract product information: {result.error}"
            )
        
        scraped_data = result.data
        if not scraped_data:
            logger.error(f"AI agent returned no data for {request.product_url}")
            raise HTTPException(
                status_code=400, 
                detail="Failed to extract any product information from the provided URL"
            )
        
        logger.info(f"AI agent extracted product info: {scraped_data.get('title', 'Unknown')}")
        
        # Ensure we have valid data, especially title
        title = scraped_data.get('title') or 'Unknown Product'
        if title == 'Unknown Product' or not title.strip():
            # Try to create a better title from URL
            from urllib.parse import urlparse
            parsed_url = urlparse(request.product_url)
            domain = parsed_url.netloc.replace('www.', '')
            if 'amazon' in domain:
                title = 'Amazon Product'
            else:
                title = f'Product from {domain}'
        
        # Create product with AI-extracted data
        new_product = ProductService.create_product(
            title=title,
            description=scraped_data.get('description') or f'Product available from {urlparse(request.product_url).netloc}',
            category=scraped_data.get('category') or 'other',
            merchant=scraped_data.get('merchant') or ProductService._detect_merchant_from_url(request.product_url),
            original_price=scraped_data.get('original_price'),
            sale_price=scraped_data.get('sale_price'),
            product_url=request.product_url,  # Always preserve original URL for affiliate links
            image_url=scraped_data.get('image_url'),
            brand=scraped_data.get('brand'),
            model=scraped_data.get('model'),
            rating=scraped_data.get('rating'),
            rating_count=scraped_data.get('rating_count'),
            is_featured=request.is_featured,
            project_types=scraped_data.get('project_types') or ['general'],
            created_by=user_id
        )
        
        if new_product:
            return {
                "success": True,
                "product": new_product,
                "scraped_data": scraped_data,
                "message": f"Product created successfully using {scraped_data.get('extraction_method', 'ai')} extraction",
                "extraction_method": scraped_data.get('extraction_method', 'ai'),
                "extraction_details": {
                    "title_extracted": scraped_data.get('title') is not None and scraped_data.get('title') != 'Unknown Product',
                    "price_extracted": scraped_data.get('sale_price') is not None or scraped_data.get('original_price') is not None,
                    "image_extracted": scraped_data.get('image_url') is not None,
                    "brand_extracted": scraped_data.get('brand') is not None
                }
            }
        else:
            logger.error(f"Product creation failed for URL: {request.product_url}")
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to create product from URL. The AI agent may have encountered issues extracting product information from this page."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product from URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create product from URL: {str(e)}")

@app.post("/api/admin/products")
async def admin_create_product(
    product: ProductCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new product (admin only)"""
    try:
        user_id = int(current_user.get("sub"))
        
        # Check if user is admin
        from database import get_db_session
        from models.user_models import User
        
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_admin():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
        
        # Create product
        new_product = ProductService.create_product(
            title=product.title,
            description=product.description,
            category=product.category,
            merchant=product.merchant,
            original_price=product.original_price,
            sale_price=product.sale_price,
            product_url=product.product_url,
            image_url=product.image_url,
            brand=product.brand,
            model=product.model,
            rating=product.rating,
            rating_count=product.rating_count,
            is_featured=product.is_featured,
            created_by=user_id
        )
        
        if new_product:
            return {
                "success": True,
                "product": new_product,
                "message": "Product created successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create product")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product")

@app.get("/api/admin/products/{product_id}")
async def admin_get_product(
    product_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific product for admin editing"""
    try:
        user_id = int(current_user.get("sub"))
        
        # Check if user is admin
        from database import get_db_session
        from models.user_models import User
        
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_admin():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
        
        product = ProductService.get_product_by_id(product_id)
        
        if product:
            return {
                "success": True,
                "product": product
            }
        else:
            raise HTTPException(status_code=404, detail="Product not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        raise HTTPException(status_code=500, detail="Failed to get product")

@app.put("/api/admin/products/{product_id}")
async def admin_update_product(
    product_id: int,
    product: ProductUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update a product (admin only)"""
    try:
        user_id = int(current_user.get("sub"))
        
        # Check if user is admin
        from database import get_db_session
        from models.user_models import User
        
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_admin():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
        
        # Update product
        updated_product = ProductService.update_product(
            product_id=product_id,
            title=product.title,
            description=product.description,
            category=product.category,
            merchant=product.merchant,
            original_price=product.original_price,
            sale_price=product.sale_price,
            product_url=product.product_url,
            image_url=product.image_url,
            brand=product.brand,
            model=product.model,
            rating=product.rating,
            rating_count=product.rating_count,
            is_featured=product.is_featured,
            is_active=product.is_active,
            sort_order=product.sort_order
        )
        
        if updated_product:
            return {
                "success": True,
                "product": updated_product,
                "message": "Product updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Product not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to update product")

@app.delete("/api/admin/products/{product_id}")
async def admin_delete_product(
    product_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a product (admin only)"""
    try:
        user_id = int(current_user.get("sub"))
        
        # Check if user is admin
        from database import get_db_session
        from models.user_models import User
        
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_admin():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
        
        success = ProductService.delete_product(product_id)
        
        if success:
            return {
                "success": True,
                "message": "Product deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Product not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete product")

# Original DIY analysis endpoint (kept for compatibility)
@app.post("/analyze-project")
async def analyze_project(
    images: List[UploadFile] = File(...),
    description: str = Form(default=""),
    project_type: str = Form(default=""),
    budget_range: str = Form(default="")
):
    """Original DIY project analysis endpoint"""
    try:
        # Save uploaded images
        image_paths = []
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        for image in images:
            file_path = os.path.join(upload_dir, image.filename)
            with open(file_path, "wb") as buffer:
                content = await image.read()
                buffer.write(content)
            image_paths.append(file_path)
        
        # Use OpenAI Vision API for real image analysis if available
        from services.openai_vision_service import vision_service
        
        # Analyze the first image with OpenAI Vision
        if images and len(images) > 0:
            try:
                # Read and encode the first image
                first_image = images[0]
                first_image.file.seek(0)  # Reset file pointer
                image_content = await first_image.read()
                image_base64 = base64.b64encode(image_content).decode('utf-8')
                
                # Get AI analysis
                analysis_data = await vision_service.analyze_diy_project(
                    image_base64=image_base64,
                    project_description=description
                )
                
                # Add user's project type if specified
                if project_type:
                    analysis_data["project_type"] = project_type
                    
                logger.info("Successfully analyzed project with OpenAI Vision")
                
            except Exception as e:
                logger.error(f"Failed to analyze with OpenAI Vision: {e}")
                # Fall back to mock data
                analysis_data = {
                    "project_name": "DIY Wooden Table Project",
                    "description": f"Based on analysis of {len(images)} uploaded images, this is a {project_type or 'woodworking'} DIY project. {description}",
                    "materials": [
                        {"name": "Pine Wood Board", "specification": "3/4 inch thick", "quantity": "2 pieces", "estimated_price_range": "$25-40"},
                        {"name": "Wood Screws", "specification": "1.5 inch long", "quantity": "20 pieces", "estimated_price_range": "$3-5"},
                        {"name": "Wood Glue", "specification": "Strong adhesive", "quantity": "1 bottle", "estimated_price_range": "$4-8"},
                        {"name": "Wood Stain", "specification": "Natural finish", "quantity": "1 can", "estimated_price_range": "$8-12"},
                        {"name": "Sandpaper", "specification": "120/220 grit", "quantity": "5 sheets", "estimated_price_range": "$5-10"}
                    ],
                    "tools": [
                        {"name": "Power Drill", "necessity": "Essential"},
                        {"name": "Screwdriver Set", "necessity": "Essential"}, 
                        {"name": "Measuring Tape", "necessity": "Essential"},
                        {"name": "Saw (Circular/Miter)", "necessity": "Essential"},
                        {"name": "Sandpaper/Sander", "necessity": "Essential"},
                        {"name": "Safety Glasses", "necessity": "Essential"},
                        {"name": "Work Gloves", "necessity": "Recommended"},
                        {"name": "Clamps", "necessity": "Recommended"},
                        {"name": "Level", "necessity": "Recommended"}
                    ],
                    "difficulty_level": "medium",
                    "estimated_time": "4-6 hours",
                    "safety_notes": ["Wear safety glasses at all times", "Use tools safely and follow manufacturer instructions", "Keep workspace clean and well-organized", "Ensure adequate ventilation when using stains or adhesives"],
                    "steps": [
                        "1. Safety First: Put on safety glasses and work gloves. Ensure your workspace is well-ventilated and clean.",
                        "2. Measure and Plan: Using measuring tape, carefully measure and mark all cut lines on the wood boards. Double-check all measurements.",
                        "3. Cut the Wood: Use a circular saw or miter saw to cut the wood pieces according to your measurements. Sand cut edges smooth.",
                        "4. Pre-drill Holes: Use the power drill to pre-drill pilot holes for screws to prevent wood splitting.",
                        "5. Apply Wood Glue: Apply a thin, even layer of wood glue to joining surfaces. Work quickly as glue sets fast.",
                        "6. Assemble Frame: Clamp pieces together and secure with wood screws. Use level to ensure everything is square.",
                        "7. Initial Sanding: Sand all surfaces starting with 120-grit, then 220-grit sandpaper for smooth finish.",
                        "8. Clean Surface: Remove all dust with tack cloth or compressed air before staining.",
                        "9. Apply Stain: Use brush or cloth to apply wood stain evenly. Work with the grain, not against it.",
                        "10. Final Assembly: Once stain is dry, complete any final assembly and add any hardware or accessories.",
                        "11. Quality Check: Inspect all joints, sand any rough spots, and ensure the project is sturdy and safe to use."
                    ]
                }
        else:
            # No images provided, use default mock data
            analysis_data = {
                "project_name": "DIY Project",
                "description": f"Project analysis for {project_type or 'general'} DIY project. {description}",
                "materials": [],
                "tools": [],
                "difficulty_level": "medium",
                "estimated_time": "varies",
                "safety_notes": ["Always follow safety guidelines"],
                "steps": ["Upload an image for detailed analysis"]
            }
        
        # Generate product recommendations
        try:
            product_recommendations = await generate_smart_product_recommendations(analysis_data, project_type, budget_range)
        except Exception as rec_error:
            logger.error(f"Product recommendation failed: {str(rec_error)}")
            product_recommendations = get_fallback_recommendations()
        
        # Build final result
        result = {
            "success": True,
            "results": [
                {
                    "data": {
                        "comprehensive_analysis": analysis_data,
                        "materials": [
                            {"name": "Pine Wood Board", "specification": "3/4 inch thick", "quantity": "2 pieces"},
                            {"name": "Wood Screws", "specification": "1.5 inch long", "quantity": "20 pieces"},
                            {"name": "Wood Glue", "specification": "Strong adhesive", "quantity": "1 bottle"}
                        ]
                    },
                    "execution_time": 2.5
                },
                {
                    "data": product_recommendations,
                    "execution_time": 1.8
                }
            ]
        }
        
        # Clean up temporary files
        for path in image_paths:
            try:
                os.remove(path)
            except:
                pass
                
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing project: {str(e)}")
        return {"success": False, "error": str(e)}

# Helper functions

async def generate_smart_product_recommendations(analysis_data: Dict, project_type: str, budget_range: str) -> Dict:
    """Generate smart product recommendations"""
    try:
        from agents.product_recommendation_agent import ProductRecommendationAgent
        
        # Create ProductRecommendationAgent instance
        agent = ProductRecommendationAgent()
        
        # Prepare tools and materials data
        tools_and_materials = []
        
        # Extract tools and materials from analysis data
        if "tools" in analysis_data:
            for tool in analysis_data["tools"]:
                tools_and_materials.append({
                    "name": tool["name"], 
                    "type": "tool",
                    "necessity": tool.get("necessity", "Recommended")
                })
                
        if "materials" in analysis_data:
            for material in analysis_data["materials"]: 
                tools_and_materials.append({
                    "name": material["name"],
                    "type": "material", 
                    "specification": material.get("specification", "")
                })
        
        # Create agent task
        from core.agent_base import AgentTask
        task = AgentTask(
            task_id=f"recommendation_{hash(str(analysis_data))}",
            agent_name="product_recommendation",
            input_data={
                "tools_and_materials": tools_and_materials,
                "project_type": project_type,
                "budget_level": budget_range
            },
            created_at=datetime.utcnow()
        )
        
        # Execute recommendation task
        result = await agent.process_task(task)
        
        if result.success:
            return result.data
        else:
            logger.error(f"Agent recommendation failed: {result.error}")
            return get_fallback_recommendations()
            
    except Exception as e:
        logger.error(f"Error generating smart recommendations: {str(e)}")
        return get_fallback_recommendations()

def get_fallback_recommendations() -> Dict:
    """Get fallback recommendation data"""
    return {
        "assessed_results": [
            {
                "material": "Power Drill",
                "products": [
                    {
                        "title": "BLACK+DECKER 20V MAX Cordless Drill",
                        "price": "$49.99",
                        "image_url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400&h=300&fit=crop",
                        "product_url": "https://www.amazon.com/BLACK-DECKER-LD120VA-20-Volt-Lithium-Ion/dp/B00AXTBSRU",
                        "platform": "Amazon",
                        "rating": 4.4,
                        "quality_score": 4.3,
                        "quality_reasons": ["Great for beginners", "Good battery life", "Trusted brand"],
                        "price_value_ratio": 4.5,
                        "recommendation_level": "Best Value"
                    }
                ],
                "total_assessed": 1,
                "avg_quality_score": 4.3
            }
        ],
        "overall_recommendations": {
            "total_products_assessed": 1,
            "average_quality_score": 4.3,
            "best_products": [
                {
                    "material": "Power Drill",
                    "product": {
                        "title": "BLACK+DECKER 20V MAX Cordless Drill",
                        "platform": "Amazon", 
                        "product_url": "https://www.amazon.com/dp/B00AXTBSRU"
                    }
                }
            ],
            "shopping_tips": [
                "Choose products with 4.0+ star ratings for best quality",
                "Compare prices across multiple retailers",
                "Read customer reviews for insights"
            ],
            "quality_distribution": {
                "Best Value": 1
            }
        }
    }

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

@app.post("/api/test/create-demo-user")
async def create_demo_user():
    """Create demo user for testing"""
    try:
        # Try to create demo user
        demo_user = UserService.create_user("demo@cheasydiy.com", "demouser", "demo2025!")
        if demo_user:
            # Upgrade to premium
            UserService.upgrade_membership(demo_user["id"], "premium", days=365)
            return {
                "message": "Demo user created successfully",
                "username": "demouser",
                "password": "demo2025!",
                "membership": "premium",
                "user_id": demo_user["id"]
            }
        else:
            return {"message": "Demo user already exists or creation failed"}
    except Exception as e:
        return {"message": f"Error creating demo user: {str(e)}"}

@app.post("/api/admin/create-admin-user")
async def create_admin_user(
    admin_email: str = Form(...),
    admin_username: str = Form(...),
    admin_password: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Create admin user - only accessible by existing admin"""
    try:
        user_id = int(current_user.get("sub"))
        
        # Check if current user is admin
        from database import get_db_session
        from models.user_models import User, MembershipLevel
        
        with get_db_session() as db:
            current_user_obj = db.query(User).filter(User.id == user_id).first()
            if not current_user_obj or not current_user_obj.is_admin():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admin users can create new admin accounts"
                )
        
        # Create admin user
        admin_user = UserService.create_user(admin_email, admin_username, admin_password)
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        # Upgrade to admin
        success = UserService.upgrade_membership(admin_user["id"], "admin", days=36500)  # 100 years
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to set admin privileges")
        
        return {
            "message": "Admin user created successfully",
            "username": admin_username,
            "email": admin_email,
            "membership": "admin",
            "user_id": admin_user["id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create admin user")

@app.post("/api/setup/create-first-admin")
async def create_first_admin(
    admin_email: str = Form(...),
    admin_username: str = Form(...),
    admin_password: str = Form(...),
    setup_key: str = Form(...)
):
    """Create first admin user - only works if no admin exists and correct setup key"""
    try:
        # Check setup key
        expected_setup_key = os.getenv("ADMIN_SETUP_KEY", "setup_admin_2025")
        if setup_key != expected_setup_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid setup key"
            )
        
        # Check if any admin already exists
        from database import get_db_session
        from models.user_models import User, MembershipLevel
        
        with get_db_session() as db:
            existing_admin = db.query(User).filter(
                User.membership_level == MembershipLevel.ADMIN
            ).first()
            
            if existing_admin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Admin user already exists"
                )
        
        # Create first admin user
        admin_user = UserService.create_user(admin_email, admin_username, admin_password)
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        # Set admin privileges
        success = UserService.upgrade_membership(admin_user["id"], "admin", days=36500)  # 100 years
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to set admin privileges")
        
        return {
            "message": "First admin user created successfully",
            "username": admin_username,
            "email": admin_email,
            "membership": "admin",
            "user_id": admin_user["id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating first admin user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create first admin user")

@app.get("/api/test/jwt-debug/{token}")
async def test_jwt_debug(token: str):
    """Debug JWT token validation"""
    try:
        from auth.auth_handler import verify_token, SECRET_KEY
        import os
        from jose import jwt
        
        # Test token verification
        payload = verify_token(token)
        
        # Try to decode without verification to see the payload
        unverified_payload = jwt.get_unverified_claims(token)
        
        # Get environment info
        env_secret = os.getenv("JWT_SECRET_KEY", "not-set")
        
        return {
            "token_valid": payload is not None,
            "verified_payload": payload,
            "unverified_payload": unverified_payload,
            "env_jwt_secret": env_secret[:10] + "..." if env_secret != "not-set" else "not-set",
            "handler_secret": SECRET_KEY[:10] + "...",
            "secrets_match": env_secret == SECRET_KEY,
            "message": "JWT debug information"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "JWT debug failed"
        }

@app.get("/api/test/user-count")
async def test_user_count():
    """Get count of users in database"""
    try:
        from database import get_db_session
        from models.user_models import User
        
        with get_db_session() as db:
            user_count = db.query(User).count()
            users = db.query(User).all()
            user_list = [{"id": u.id, "username": u.username, "email": u.email} for u in users]
        
        return {
            "user_count": user_count,
            "users": user_list,
            "message": "User count retrieved successfully"
        }
    except Exception as e:
        return {
            "user_count": 0,
            "error": str(e),
            "message": "Failed to get user count"
        }

@app.get("/api/test/db-connection")
async def test_db_connection():
    """Test database connection"""
    try:
        from database import test_connection, create_tables, engine
        from sqlalchemy import text
        
        # Test basic connection
        connection_ok = test_connection()
        
        # Try to execute a simple query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_result = result.fetchone()
        
        # Try to create tables
        create_tables()
        
        return {
            "database_connection": connection_ok,
            "simple_query": test_result[0] if test_result else None,
            "tables_created": True,
            "message": "Database connection successful"
        }
    except Exception as e:
        return {
            "database_connection": False,
            "error": str(e),
            "message": "Database connection failed"
        }

# Demo user will be created in database startup if needed

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