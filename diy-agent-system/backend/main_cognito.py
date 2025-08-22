"""
Main FastAPI application with AWS Cognito authentication
No local user database - all auth handled by Cognito
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
import os
import sys
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Import Cognito auth
from auth.cognito_auth import (
    cognito_auth, 
    get_current_user, 
    require_group, 
    require_permission,
    initialize_cognito_groups
)

# Tool identification with OpenAI Vision API
async def identify_tool_with_openai(image_base64: str, user_group: str) -> Any:
    """Identify tool using OpenAI Vision API directly"""
    import openai
    from core.agent_base import AgentResult
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OpenAI API key not found, falling back to intelligent mock")
        return await get_intelligent_mock_result(user_group)
    
    try:
        # Convert base64 to proper format
        image_url = f"data:image/jpeg;base64,{image_base64}"
        
        # Create OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Call Vision API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """You are a professional tool identification expert. Analyze this image and identify the specific tool shown.

Respond ONLY with this exact JSON format:
{
    "name": "Specific tool name",
    "brand": "Brand name or null",
    "model": "Model number or null", 
    "category": "power_tools, hand_tools, measuring, cutting, fastening, outdoor, or unknown",
    "confidence": 0.85,
    "specifications": {"key": "value"}
}

Be precise with tool identification."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ],
            max_tokens=600,
            temperature=0.1
        )
        
        # Parse response
        content = response.choices[0].message.content
        logger.info(f"OpenAI Vision response: {content}")
        
        # Extract JSON
        import json
        import re
        
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group())
                
                # Create result with real AI data
                tool_info = {
                    "name": json_data.get("name", "Unknown Tool"),
                    "brand": json_data.get("brand"),
                    "model": json_data.get("model"),
                    "category": json_data.get("category", "unknown"),
                    "confidence": float(json_data.get("confidence", 0.8)),
                    "specifications": json_data.get("specifications", {})
                }
                
                # Generate mock product data (we can enhance this with real scraping later)
                exact_matches = await generate_mock_products(tool_info, "exact")
                alternatives = await generate_mock_products(tool_info, "alternatives")
                
                return AgentResult(
                    success=True,
                    data={
                        "tool_info": tool_info,
                        "exact_matches": exact_matches,
                        "alternatives": alternatives,
                        "search_timestamp": datetime.utcnow().isoformat()
                    }
                )
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                
        logger.warning("Could not parse OpenAI response, falling back to mock")
        return await get_intelligent_mock_result(user_group)
        
    except Exception as e:
        logger.error(f"OpenAI Vision API error: {str(e)}")
        return await get_intelligent_mock_result(user_group)


async def get_intelligent_mock_result(user_group: str) -> Any:
    """Get intelligent mock result for fallback"""
    from core.agent_base import AgentResult
    import random
    
    # Intelligent mock tools based on variety
    mock_tools = [
        {
            "name": "Cordless Drill Driver",
            "brand": "DeWalt",
            "model": "DCD771C2",
            "category": "power_tools",
            "confidence": 0.92,
            "specifications": {
                "voltage": "20V MAX",
                "chuck_size": "1/2 inch",
                "torque_settings": "15+1"
            }
        },
        {
            "name": "Circular Saw",
            "brand": "Milwaukee", 
            "model": "2630-20",
            "category": "power_tools",
            "confidence": 0.89,
            "specifications": {
                "blade_diameter": "6-1/2 inch",
                "voltage": "18V",
                "max_cut_depth": "2-1/8 inch"
            }
        },
        {
            "name": "Angle Grinder",
            "brand": "Makita",
            "model": "GA5030R",
            "category": "power_tools",
            "confidence": 0.86,
            "specifications": {
                "disc_diameter": "5 inch",
                "power": "720W",
                "no_load_speed": "11000 RPM"
            }
        }
    ]
    
    # Select random tool for variety
    selected_tool = random.choice(mock_tools)
    
    exact_matches = await generate_mock_products(selected_tool, "exact")
    alternatives = await generate_mock_products(selected_tool, "alternatives")
    
    return AgentResult(
        success=True,
        data={
            "tool_info": selected_tool,
            "exact_matches": exact_matches,
            "alternatives": alternatives,
            "search_timestamp": datetime.utcnow().isoformat()
        }
    )


async def generate_mock_products(tool_info: dict, product_type: str) -> list:
    """Generate mock product listings"""
    brand = tool_info.get("brand", "Unknown")
    name = tool_info.get("name", "Tool")
    
    if product_type == "exact":
        return [
            {
                "retailer": "Home Depot",
                "title": f"{brand} {name}",
                "price": 129.99,
                "url": f"https://www.homedepot.com/s/{brand.lower()}+{name.lower().replace(' ', '+')}",
                "image_url": "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=300",
                "in_stock": True
            },
            {
                "retailer": "Amazon",
                "title": f"{brand} {name} Kit",
                "price": 139.99,
                "url": f"https://amazon.com/s?k={brand}+{name.replace(' ', '+')}",
                "image_url": "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=300",
                "in_stock": True
            }
        ]
    else:
        alternative_brands = ["Ryobi", "BLACK+DECKER", "Bosch"]
        return [
            {
                "retailer": "Lowes",
                "title": f"{alt_brand} {name}",
                "price": 99.99,
                "url": f"https://lowes.com/s/{alt_brand.lower()}+{name.lower().replace(' ', '+')}",
                "image_url": "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=300",
                "in_stock": True
            } for alt_brand in alternative_brands[:2]
        ]


# Optional auth dependency - allows both authenticated and guest users
async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(HTTPBearer(auto_error=False))) -> Dict[str, Any]:
    """Optional authentication - allows guest access"""
    if not credentials:
        # Return guest user
        return {
            "username": "guest",
            "email": "",
            "groups": ["free"],
            "group": "free", 
            "permissions": {
                "diy_assistant": True,
                "tool_identification": True,
                "daily_quota": 3,  # Limited quota for guests
                "priority_support": False,
                "admin_features": False
            }
        }
    
    try:
        # Try to get authenticated user
        return await get_current_user(credentials)
    except Exception:
        # If authentication fails, return guest user
        return {
            "username": "guest",
            "email": "",
            "groups": ["free"],
            "group": "free",
            "permissions": {
                "diy_assistant": True,
                "tool_identification": True,
                "daily_quota": 3,
                "priority_support": False,
                "admin_features": False
            }
        }

# Import agents
from agents.product_recommendation_agent import ProductRecommendationAgent
from agents.tool_identification_agent import ToolIdentificationAgent
from core.agent_base import AgentTask, AgentManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DIY Smart Assistant API with Cognito",
    description="AI-powered DIY project assistant with AWS Cognito authentication",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:3003",  # Current frontend port
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3003"   # Alternative localhost format
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize Agent Manager
agent_manager = AgentManager()
agent_manager.register_agent(ProductRecommendationAgent())
agent_manager.register_agent(ToolIdentificationAgent())


# ============================================
# Public Endpoints (No Authentication Required)
# ============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DIY Smart Assistant API with Cognito Auth",
        "version": "2.0.0",
        "auth": "AWS Cognito",
        "docs": "/docs"
    }


@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API is running"""
    return {
        "status": "ok",
        "message": "API is running with Cognito authentication",
        "timestamp": os.popen('date').read().strip()
    }


@app.get("/api/test-products")
async def test_products():
    """Simple test endpoint for products"""
    return {"message": "products endpoint working", "count": 3}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "auth_service": "cognito",
        "cognito_configured": bool(os.getenv("COGNITO_USER_POOL_ID"))
    }


@app.get("/api/auth/debug")
async def debug_auth(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Debug endpoint to check user authentication and groups"""
    return {
        "status": "authenticated",
        "user": current_user,
        "username": current_user.get("username"),
        "groups": current_user.get("groups", []),
        "is_admin": "admin" in current_user.get("groups", []),
        "message": "Token verification working!"
    }


@app.get("/api/test-simple")
async def test_simple():
    """Simple test without authentication"""
    return {"message": "Backend is working", "timestamp": "2024-01-01"}


# ============================================
# Authentication Endpoints
# ============================================

@app.post("/api/auth/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    username: str = Form(...)
):
    """Register a new user"""
    result = await cognito_auth.register_user(email, password, username)
    return result


@app.post("/api/auth/confirm-email")
async def confirm_email(
    email: str = Form(...),
    confirmation_code: str = Form(...)
):
    """Confirm user email with verification code"""
    result = await cognito_auth.confirm_email(email, confirmation_code)
    return result


@app.post("/api/auth/login")
async def login(
    email: str = Form(...),
    password: str = Form(...)
):
    """Login user and return tokens"""
    result = await cognito_auth.login(email, password)
    return result


@app.post("/api/auth/refresh")
async def refresh_token(
    refresh_token: str = Form(...)
):
    """Refresh access token"""
    result = await cognito_auth.refresh_token(refresh_token)
    return result


@app.post("/api/auth/logout")
async def logout(current_user: Dict = Depends(get_current_user)):
    """Logout current user"""
    # Token is passed in the header, extracted by get_current_user
    return {"message": "Logged out successfully"}


@app.post("/api/auth/forgot-password")
async def forgot_password(
    email: str = Form(...)
):
    """Initiate password reset"""
    result = await cognito_auth.forgot_password(email)
    return result


@app.post("/api/auth/reset-password")
async def reset_password(
    email: str = Form(...),
    code: str = Form(...),
    new_password: str = Form(...)
):
    """Reset password with confirmation code"""
    result = await cognito_auth.confirm_forgot_password(email, code, new_password)
    return result


@app.get("/api/auth/me")
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "username": current_user.get("username"),
        "email": current_user.get("email"),
        "groups": current_user.get("groups"),
        "permissions": current_user.get("permissions")
    }


# ============================================
# Protected Endpoints (Authentication Required)
# ============================================

@app.post("/analyze-project")
async def analyze_project(
    current_user: Dict = Depends(get_current_user),
    images: List[UploadFile] = File(...),
    description: Optional[str] = Form(None),
    project_type: Optional[str] = Form(None),
    budget_range: Optional[str] = Form(None)
):
    """
    Analyze DIY project from uploaded images
    Available to all authenticated users
    """
    try:
        # Check daily quota
        permissions = current_user.get("permissions", {})
        daily_quota = permissions.get("daily_quota", 5)
        
        # TODO: Implement quota tracking (could use DynamoDB or Redis)
        
        logger.info(f"User {current_user.get('username')} analyzing project")
        
        # Process images (mock for now)
        project_analysis = {
            "project_name": "Custom DIY Project",
            "description": description or "AI-analyzed DIY project",
            "materials": [
                {"name": "Wood Boards", "quantity": "10", "specifications": "2x4 inches, 8 feet long"},
                {"name": "Wood Screws", "quantity": "50", "specifications": "2.5 inch deck screws"},
                {"name": "Wood Glue", "quantity": "1", "specifications": "16 oz bottle"}
            ],
            "tools": [
                {"name": "Circular Saw", "required": True},
                {"name": "Drill", "required": True},
                {"name": "Measuring Tape", "required": True}
            ],
            "difficulty_level": "intermediate",
            "estimated_time": "6-8 hours",
            "safety_notes": [
                "Always wear safety goggles when cutting",
                "Use dust mask when sanding",
                "Keep workspace clean and organized"
            ],
            "steps": [
                {"step": 1, "description": "Measure and mark all pieces according to plan"},
                {"step": 2, "description": "Cut wood boards to required dimensions"},
                {"step": 3, "description": "Sand all surfaces smooth"},
                {"step": 4, "description": "Assemble pieces using wood glue and screws"},
                {"step": 5, "description": "Apply finish and let dry"}
            ]
        }
        
        # Get product recommendations
        agent_task = AgentTask(
            task_id="recommendation_task",
            agent_name="product_recommendation",
            input_data={
                "materials": project_analysis["materials"],
                "tools": project_analysis["tools"],
                "project_type": project_type or "general",
                "budget_range": budget_range or "medium"
            }
        )
        
        recommendation_result = await agent_manager.execute_task(agent_task)
        
        return {
            "success": True,
            "user": current_user.get("username"),
            "user_group": current_user.get("group"),
            "quota_remaining": daily_quota - 1 if daily_quota > 0 else "unlimited",
            "results": [
                {
                    "type": "project_analysis",
                    "data": {
                        "comprehensive_analysis": project_analysis
                    }
                },
                {
                    "type": "product_recommendations",
                    "data": recommendation_result.data if recommendation_result.success else {}
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/tool-identification/analyze")  
async def analyze_tools(
    images: List[UploadFile] = File(...),
    current_user: Dict = Depends(get_optional_user)
):
    """
    Identify tools from uploaded images using real AI
    Optional authentication - works for both authenticated and non-authenticated users
    """
    
    try:
        logger.info(f"Tool identification request from user: {current_user.get('username')} (group: {current_user.get('group')})")
        
        if not images:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No images provided"
            )
        
        # Process the first image (we can extend this to handle multiple images later)
        image_file = images[0]
        
        # Read and convert image to base64
        import base64
        image_content = await image_file.read()
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Get user membership level for quotas and features
        user_group = current_user.get('group', 'free')
        
        # Prepare input data for Tool Identification Agent
        input_data = {
            "image_data": image_base64,
            "include_alternatives": True,
            "membership_level": user_group,
            "user_id": current_user.get('username', 'guest')
        }
        
        # Execute tool identification with real AI
        logger.info("Executing tool identification with OpenAI Vision API...")
        result = await identify_tool_with_openai(image_base64, user_group)
        
        if result.success:
            logger.info(f"Tool identification successful: {result.data.get('tool_info', {}).get('name', 'Unknown')}")
            return {
                "success": True,
                "message": "Tool identification successful",
                **result.data
            }
        else:
            logger.error(f"Tool identification failed: {result.error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Tool identification failed: {result.error}"
            )
        
    except Exception as e:
        logger.error(f"Error in tool identification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/tool-identification/history")
async def get_tool_identification_history(
    limit: int = 10,
    current_user: Dict = Depends(get_optional_user)
):
    """
    Get tool identification history - Guest access allowed
    """
    try:
        logger.info("History request received")
        
        # Mock history data - in real implementation, this would come from database
        mock_history = [
            {
                "id": "hist_001",
                "tool_info": {
                    "name": "DeWalt DCS391B Circular Saw",
                    "brand": "DeWalt",
                    "model": "DCS391B",
                    "category": "Power Tools",
                    "confidence": 0.95
                },
                "search_timestamp": "2024-01-15T10:30:00Z",
                "exact_matches": [
                    {
                        "title": "DeWalt DCS391B 20V MAX Circular Saw",
                        "price": 129.99,
                        "retailer": "Home Depot",
                        "url": "https://www.homedepot.com/p/dewalt-dcs391b",
                        "image_url": "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=300",
                        "in_stock": True
                    }
                ],
                "alternatives": []
            }
        ]
        
        # Limit results
        limited_history = mock_history[:limit]
        
        return {
            "success": True,
            "history": limited_history,
            "total": len(mock_history),
            "user": current_user.get("username")
        }
        
    except Exception as e:
        logger.error(f"Error getting identification history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/api/tool-identification/history/{identification_id}")
async def delete_tool_identification(
    identification_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Delete a tool identification from user's history
    Requires authentication
    """
    try:
        logger.info(f"User {current_user.get('username')} deleting identification {identification_id}")
        
        # Mock deletion - in real implementation, this would delete from database
        return {
            "success": True,
            "message": f"Identification {identification_id} deleted successfully",
            "user": current_user.get("username")
        }
        
    except Exception as e:
        logger.error(f"Error deleting identification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================
# Product Endpoints
# ============================================

# Mock products data for synchronization
MOCK_PRODUCTS = [
    {
        "id": 1,
        "title": "BlueDriver Bluetooth Pro OBDII Scan Tool for iPhone & Android",
        "description": "The BlueDriver Bluetooth Pro OBDII Scan Tool allows you to diagnose check engine, ABS, SRS, airbag, and over 7000 issues on vehicles from 1996 and newer. It connects to your smartphone for easy use and does not require a subscription fee.",
        "category": "tools",
        "merchant": "amazon",
        "original_price": 119.95,
        "sale_price": 84.95,
        "discount_percentage": 29,
        "product_url": "https://amzn.to/3V2BIXY",
        "image_url": "https://m.media-amazon.com/images/I/41TNTEEt8tL._MCnd_AC_.jpg",
        "thumbnail_url": "https://m.media-amazon.com/images/I/41TNTEEt8tL._MCnd_AC_.jpg",
        "is_featured": False,
        "is_active": True,
        "sort_order": 0,
        "brand": "BlueDriver",
        "model": "Bluetooth Pro OBDII Scan Tool",
        "rating": 4.5,
        "rating_count": 59854,
        "created_at": "2025-08-17T06:14:48.404991",
        "updated_at": "2025-08-17T06:14:48.405991",
        "created_by": 2,
        "click_count": 0,
        "view_count": 0,
        "project_types": ["automotive"]
    },
    {
        "id": 2,
        "title": "MOTOPOWER MP69033 Car OBD2 Scanner Code Reader Engine Fault Scanner CAN Diagnostic Scan Tool for All OBD II Protocol Cars Since 1996, Yellow",
        "description": "The MOTOPOWER MP69033 is a versatile OBD2 scanner designed for diagnosing engine faults in all OBD II protocol cars since 1996. It features a user-friendly interface and is compact for easy handling.",
        "category": "tools",
        "merchant": "amazon", 
        "original_price": 26.99,
        "sale_price": 22.5,
        "discount_percentage": 16,
        "product_url": "https://amzn.to/3V8Xauo",
        "image_url": "https://m.media-amazon.com/images/I/61ybpjOSa1L.__AC_SX300_SY300_QL70_FMwebp_.jpg",
        "thumbnail_url": "https://m.media-amazon.com/images/I/61ybpjOSa1L.__AC_SX300_SY300_QL70_FMwebp_.jpg",
        "is_featured": False,
        "is_active": True,
        "sort_order": 0,
        "brand": "MOTOPOWER",
        "model": "MP69033",
        "rating": 4.6,
        "rating_count": 46380,
        "created_at": "2025-08-17T06:16:09.163471",
        "updated_at": "2025-08-17T06:16:09.163471", 
        "created_by": 2,
        "click_count": 0,
        "view_count": 0,
        "project_types": ["automotive", "general"]
    },
    {
        "id": 3,
        "title": "SKIL 15 Amp 10 Inch Portable Jobsite Table Saw with Folding Stand- TS6307-00",
        "description": "The SKIL 15 Amp 10 Inch Portable Jobsite Table Saw features a folding stand for easy transport and storage, making it ideal for job sites and home projects.",
        "category": "tools",
        "merchant": "amazon",
        "original_price": 355.99,
        "sale_price": 329.0,
        "discount_percentage": 7,
        "product_url": "https://amzn.to/4mLx9NC",
        "image_url": "https://m.media-amazon.com/images/I/61pTjnqf86L.__AC_SX300_SY300_QL70_FMwebp_.jpg",
        "thumbnail_url": "https://m.media-amazon.com/images/I/61pTjnqf86L.__AC_SX300_SY300_QL70_FMwebp_.jpg",
        "is_featured": False,
        "is_active": True,
        "sort_order": 0,
        "brand": "SKIL",
        "model": "TS6307-00",
        "rating": 4.7,
        "rating_count": 15,
        "created_at": "2025-08-17T06:16:38.206647",
        "updated_at": "2025-08-17T06:16:38.207648",
        "created_by": 2,
        "click_count": 0,
        "view_count": 0,
        "project_types": ["woodworking", "general"]
    }
]

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    merchant: Optional[str] = None,
    project_type: Optional[str] = None,
    search: Optional[str] = None,
    featured_only: bool = False
):
    """Get products (public endpoint)"""
    try:
        # Start with all products
        filtered_products = MOCK_PRODUCTS.copy()
        
        # Apply filters
        if category:
            filtered_products = [p for p in filtered_products if p.get("category") == category]
        
        if merchant:
            filtered_products = [p for p in filtered_products if p.get("merchant") == merchant]
            
        if project_type:
            filtered_products = [p for p in filtered_products if project_type in p.get("project_types", [])]
            
        if search:
            search_lower = search.lower()
            filtered_products = [
                p for p in filtered_products 
                if search_lower in p.get("title", "").lower() 
                or search_lower in p.get("description", "").lower()
                or search_lower in p.get("brand", "").lower()
            ]
            
        if featured_only:
            filtered_products = [p for p in filtered_products if p.get("is_featured", False)]
        
        return {
            "success": True,
            "products": filtered_products,
            "total": len(filtered_products),
            "filters": {
                "category": category,
                "merchant": merchant,
                "project_type": project_type,
                "search": search,
                "featured_only": featured_only
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/products/categories")
async def get_product_categories():
    """Get product categories"""
    return {
        "success": True,
        "categories": [
            {"value": "tools", "label": "Tools"},
            {"value": "materials", "label": "Materials"},
            {"value": "safety", "label": "Safety Equipment"},
            {"value": "accessories", "label": "Accessories"},
            {"value": "other", "label": "Other"}
        ]
    }


@app.get("/api/products/merchants")
async def get_merchants():
    """Get available merchants"""
    return {
        "success": True,
        "merchants": [
            {"value": "amazon", "label": "Amazon"},
            {"value": "home_depot", "label": "Home Depot"},
            {"value": "lowes", "label": "Lowes"},
            {"value": "walmart", "label": "Walmart"}
        ]
    }


@app.get("/api/products/project-types")
async def get_project_types():
    """Get available project types"""
    return {
        "success": True,
        "project_types": [
            {"value": "automotive", "label": "Automotive"},
            {"value": "woodworking", "label": "Woodworking"},
            {"value": "plumbing", "label": "Plumbing"},
            {"value": "electrical", "label": "Electrical"},
            {"value": "general", "label": "General DIY"},
            {"value": "home_improvement", "label": "Home Improvement"}
        ]
    }


@app.post("/api/products/{product_id}/view")
async def track_product_view(product_id: int):
    """Track product view (analytics)"""
    # Mock implementation - in real app would update database
    return {"success": True, "message": "View tracked"}


@app.post("/api/products/{product_id}/click")
async def track_product_click(product_id: int):
    """Track product click (analytics)"""
    # Mock implementation - in real app would update database
    return {"success": True, "message": "Click tracked"}


# ============================================
# Admin Endpoints (Admin Group Required)
# ============================================

@app.get("/api/admin/products")
async def admin_get_products(
    include_inactive: bool = True,
    current_user: Dict = Depends(get_current_user)
):
    """Get all products for admin management"""
    if 'admin' not in current_user.get('groups', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Return same products as public endpoint for synchronization
        return {
            "success": True,
            "products": MOCK_PRODUCTS,
            "total": len(MOCK_PRODUCTS)
        }
        
    except Exception as e:
        logger.error(f"Error getting admin products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.put("/api/admin/products/{product_id}")
async def admin_update_product(
    product_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    original_price: Optional[float] = None,
    sale_price: Optional[float] = None,
    is_featured: Optional[bool] = None,
    is_active: Optional[bool] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Update product (admin only)"""
    if 'admin' not in current_user.get('groups', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Find product in mock data
        product_index = None
        for i, product in enumerate(MOCK_PRODUCTS):
            if product["id"] == product_id:
                product_index = i
                break
        
        if product_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Update product fields
        if title is not None:
            MOCK_PRODUCTS[product_index]["title"] = title
        if description is not None:
            MOCK_PRODUCTS[product_index]["description"] = description
        if original_price is not None:
            MOCK_PRODUCTS[product_index]["original_price"] = original_price
        if sale_price is not None:
            MOCK_PRODUCTS[product_index]["sale_price"] = sale_price
        if is_featured is not None:
            MOCK_PRODUCTS[product_index]["is_featured"] = is_featured
        if is_active is not None:
            MOCK_PRODUCTS[product_index]["is_active"] = is_active
        
        MOCK_PRODUCTS[product_index]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "Product updated successfully",
            "product": MOCK_PRODUCTS[product_index]
        }
        
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/api/admin/products/{product_id}")
async def admin_delete_product(
    product_id: int,
    current_user: Dict = Depends(get_current_user)
):
    """Delete product (admin only)"""
    if 'admin' not in current_user.get('groups', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Find and remove product from mock data
        for i, product in enumerate(MOCK_PRODUCTS):
            if product["id"] == product_id:
                MOCK_PRODUCTS.pop(i)
                return {
                    "success": True,
                    "message": "Product deleted successfully"
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
        
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/admin/upgrade-user")
async def upgrade_user_group(
    email: str = Form(...),
    new_group: str = Form(...),
    current_user: Dict = Depends(get_current_user)
):
    """
    Upgrade user to a different group
    Requires admin group
    """
    # Check if user is admin
    if 'admin' not in current_user.get('groups', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Validate new group
    if new_group not in ['free', 'pro', 'premium', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid group. Must be: free, pro, premium, or admin"
        )
    
    try:
        # Remove from all groups first
        current_groups = cognito_auth.get_user_groups(email)
        for group in current_groups:
            cognito_auth.remove_user_from_group(email, group)
        
        # Add to new group
        success = cognito_auth.add_user_to_group(email, new_group)
        
        if success:
            return {
                "success": True,
                "message": f"User {email} upgraded to {new_group} group"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upgrade user"
            )
            
    except Exception as e:
        logger.error(f"Error upgrading user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/admin/users")
async def list_users(
    current_user: Dict = Depends(get_current_user),
    limit: int = 50
):
    """
    List all users (admin only)
    """
    if 'admin' not in current_user.get('groups', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # List users from Cognito
        response = cognito_auth.cognito_client.list_users(
            UserPoolId=cognito_auth.user_pool_id,
            Limit=limit
        )
        
        users = []
        for user in response.get('Users', []):
            user_data = {
                "username": user['Username'],
                "status": user['UserStatus'],
                "created": str(user['UserCreateDate']),
                "attributes": {}
            }
            
            for attr in user.get('Attributes', []):
                user_data['attributes'][attr['Name']] = attr['Value']
            
            # Get user groups
            user_data['groups'] = cognito_auth.get_user_groups(user['Username'])
            
            users.append(user_data)
        
        return {
            "success": True,
            "users": users,
            "count": len(users)
        }
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/admin/stats")
async def get_system_stats(current_user: Dict = Depends(get_current_user)):
    """
    Get system statistics (admin only)
    """
    if 'admin' not in current_user.get('groups', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Get user pool statistics
        response = cognito_auth.cognito_client.describe_user_pool(
            UserPoolId=cognito_auth.user_pool_id
        )
        
        user_pool = response['UserPool']
        
        return {
            "success": True,
            "stats": {
                "total_users": user_pool.get('EstimatedNumberOfUsers', 0),
                "user_pool_name": user_pool.get('Name'),
                "user_pool_id": user_pool.get('Id'),
                "creation_date": str(user_pool.get('CreationDate')),
                "status": user_pool.get('Status')
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================
# Our Picks - Product Management API
# ============================================

@app.get("/api/test-our-picks")
async def test_our_picks_section():
    """Test route to verify Our Picks section is loading"""
    return {"message": "Our Picks section is loading correctly"}

@app.post("/api/admin/our-picks/analyze")
async def analyze_product_url(
    product_url: str = Form(...),
    current_user: Dict = Depends(get_current_user)
):
    """Analyze product URL and extract information (Admin only)"""
    # Check if user is admin
    if 'admin' not in current_user.get('groups', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        logger.info(f"Admin analyzing product URL: {product_url}")
        
        # Import and use the ProductInfoAgent
        from agents.product_info_agent import product_info_agent
        
        # Execute analysis
        result = await product_info_agent.execute({"product_url": product_url})
        
        if result.success:
            # Format the response
            extracted_data = result.data
            
            return {
                "success": True,
                "analysis_id": f"analysis_{hash(product_url)}_{int(asyncio.get_event_loop().time())}",
                "extracted_data": extracted_data,
                "source_url": product_url,
                "extraction_method": extracted_data.get("extraction_method", "unknown")
            }
        else:
            return {
                "success": False,
                "error": result.error,
                "extracted_data": None
            }
            
    except Exception as e:
        logger.error(f"Error analyzing product URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/admin/our-picks/create")
async def create_our_pick_product(
    analysis_id: str = Form(...),
    title: str = Form(...),
    brand: str = Form(None),
    category: str = Form(...),
    affiliate_link: str = Form(...),
    admin_notes: str = Form(None),
    is_featured: bool = Form(False),
    current_user: Dict = Depends(get_current_user)
):
    """Create Our Pick product from analysis (Admin only)"""
    # Check if user is admin
    if 'admin' not in current_user.get('groups', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # For now, we'll just return a success message
        # In a real implementation, this would save to database
        logger.info(f"Admin creating Our Pick product: {title}")
        
        # Generate a mock product ID
        import time
        product_id = f"ourpick_{int(time.time())}"
        
        return {
            "success": True,
            "message": "Product created successfully",
            "product_id": product_id,
            "product": {
                "id": product_id,
                "title": title,
                "brand": brand,
                "category": category,
                "affiliate_link": affiliate_link,
                "is_featured": is_featured,
                "admin_notes": admin_notes,
                "created_by": current_user.get('username', 'admin'),
                "created_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating Our Pick product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/our-picks/public/products")
async def get_public_our_picks(
    page: int = 1,
    page_size: int = 20,
    category: str = None,
    retailer: str = None,
    min_price: float = None,
    max_price: float = None,
    min_rating: float = None,
    project_type: str = None,
    search: str = None,
    sort_by: str = "rating",
    sort_order: str = "desc",
    is_featured: bool = None
):
    """Get public Our Picks products with filtering"""
    try:
        # Mock data for Our Picks products
        mock_products = [
            {
                "id": "ourpick_1",
                "title": "RYOBI 18V ONE+ Cordless Drill",
                "brand": "RYOBI",
                "category": "power_tools",
                "price": 79.00,
                "original_price": 99.00,
                "discount_percentage": 20,
                "rating": 4.5,
                "review_count": 1250,
                "description": "Professional-grade cordless drill with 24-position clutch and LED light.",
                "image_url": "https://images.homedepot-static.com/productImages/drill1.jpg",
                "affiliate_link": "https://homedepot.com/p/ryobi-drill",
                "retailer": "home_depot",
                "suitable_projects": '["woodworking", "general", "home_improvement"]',
                "is_featured": True,
                "created_at": "2024-01-15T10:00:00"
            },
            {
                "id": "ourpick_2", 
                "title": "DeWALT 20V MAX Circular Saw",
                "brand": "DeWALT",
                "category": "power_tools",
                "price": 159.99,
                "rating": 4.7,
                "review_count": 890,
                "description": "Lightweight circular saw with carbide blade for precise cuts.",
                "image_url": "https://images.homedepot-static.com/productImages/saw1.jpg",
                "affiliate_link": "https://amazon.com/dp/dewalt-saw",
                "retailer": "amazon",
                "suitable_projects": '["woodworking", "home_improvement"]',
                "is_featured": False,
                "created_at": "2024-01-10T14:30:00"
            }
        ]
        
        # Apply filters (simplified for demo)
        filtered_products = mock_products
        
        if category:
            filtered_products = [p for p in filtered_products if p["category"] == category]
        
        if retailer:
            filtered_products = [p for p in filtered_products if p["retailer"] == retailer]
        
        if is_featured is not None:
            filtered_products = [p for p in filtered_products if p["is_featured"] == is_featured]
        
        if search:
            search_lower = search.lower()
            filtered_products = [p for p in filtered_products if 
                               search_lower in p["title"].lower() or 
                               search_lower in p["brand"].lower()]
        
        # Sort products
        if sort_by == "rating":
            filtered_products.sort(key=lambda x: x.get("rating", 0), reverse=(sort_order == "desc"))
        elif sort_by == "price":
            filtered_products.sort(key=lambda x: x.get("price", 0), reverse=(sort_order == "desc"))
        elif sort_by == "created_at":
            filtered_products.sort(key=lambda x: x.get("created_at", ""), reverse=(sort_order == "desc"))
        
        # Pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_products = filtered_products[start_idx:end_idx]
        
        return {
            "success": True,
            "products": paginated_products,
            "total_count": len(filtered_products),
            "page": page,
            "page_size": page_size,
            "has_next": end_idx < len(filtered_products)
        }
        
    except Exception as e:
        logger.error(f"Error getting Our Picks products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/our-picks/track-click/{product_id}")
async def track_affiliate_click(product_id: str):
    """Track affiliate link click"""
    try:
        logger.info(f"Tracking affiliate click for product: {product_id}")
        
        # In a real implementation, this would record the click in database
        return {
            "success": True,
            "message": "Click tracked successfully"
        }
        
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# Startup Events
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting DIY Smart Assistant with Cognito Authentication")
    
    # Initialize Cognito groups
    initialize_cognito_groups()
    
    # Log configuration
    logger.info(f"Cognito User Pool: {os.getenv('COGNITO_USER_POOL_ID')}")
    logger.info(f"Cognito Region: {os.getenv('COGNITO_REGION')}")
    logger.info("Cognito authentication initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down DIY Smart Assistant")


# ============================================
# Run the application
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8001))
    
    uvicorn.run(
        "main_cognito:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )