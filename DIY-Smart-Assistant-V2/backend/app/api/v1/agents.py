"""
Agents API endpoints
"""

import logging
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from ...database import get_db
from ...models.user import User
from ...core.auth import get_current_user, get_optional_user
from ...agents.base import agent_manager
from ...agents.tool_identification import ToolIdentificationAgent
from ...agents.admin_product_analysis import AdminProductAnalysisAgent
from ...agents.user_product_recommendation import UserProductRecommendationAgent
from ...agents.project_analysis import ProjectAnalysisAgent
from ...agents.smart_tool_finder_agent import SmartToolFinderAgent
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Add OPTIONS support for CORS preflight requests
@router.options("/tool-identification/analyze")
@router.options("/project/analyze")
@router.options("/admin-product-analysis/analyze")
@router.options("/smart-tool-finder/chat")
async def options_handler():
    """Handle CORS preflight requests"""
    return {"message": "OK"}

# Initialize and register agents
tool_agent = ToolIdentificationAgent()
admin_product_agent = AdminProductAnalysisAgent()
user_product_agent = UserProductRecommendationAgent()
project_agent = ProjectAnalysisAgent()
smart_tool_finder_agent = SmartToolFinderAgent()

agent_manager.register_agent(tool_agent)
agent_manager.register_agent(admin_product_agent)
agent_manager.register_agent(user_product_agent)
agent_manager.register_agent(project_agent)
agent_manager.register_agent(smart_tool_finder_agent)


@router.post("/tool-identification/analyze")
async def identify_tool(
    image: UploadFile = File(...),
    include_alternatives: bool = Form(True),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Identify a tool from an uploaded image"""
    
    # Check file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Check file size (max 10MB)
    if image.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file too large (max 10MB)"
        )
    
    try:
        # Save image temporarily
        image_data = await image.read()
        
        # Execute tool identification
        result = await agent_manager.execute_task(
            "tool_identification",
            {
                "image_data": image_data,
                "image_path": image.filename,
                "include_alternatives": include_alternatives
            }
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error or "Tool identification failed"
            )
        
        # Add user context if authenticated
        if current_user:
            result.data["user_context"] = {
                "user_type": current_user.user_type,
                "personalized": True
            }
        
        return {
            "success": True,
            "data": result.data,
            "execution_time": result.execution_time
        }
        
    except Exception as e:
        logger.error(f"Tool identification error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/admin-product-analysis/analyze")
async def analyze_product_for_admin(
    project_type: str = Form(...),
    budget_range: str = Form("medium"),
    skill_level: str = Form("intermediate"),
    materials: Optional[str] = Form(None),
    tools_needed: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get product recommendations for a DIY project"""
    
    try:
        # Parse materials and tools if provided
        materials_list = materials.split(",") if materials else []
        tools_list = tools_needed.split(",") if tools_needed else []
        
        # Execute admin product analysis
        result = await agent_manager.execute_task(
            "admin_product_analysis",
            {
                "project_type": project_type,
                "budget_range": budget_range,
                "skill_level": skill_level,
                "materials": [m.strip() for m in materials_list],
                "tools_needed": [t.strip() for t in tools_list]
            }
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error or "Product recommendation failed"
            )
        
        # Add user context if authenticated
        if current_user:
            result.data["user_context"] = {
                "user_type": current_user.user_type,
                "personalized": True
            }
            
            # Adjust recommendations based on user type
            if current_user.user_type == "premium":
                result.data["shopping_tips"].append("Premium members get exclusive discounts")
            elif current_user.user_type == "pro":
                result.data["shopping_tips"].append("Pro members get priority support")
        
        return {
            "success": True,
            "data": result.data,
            "execution_time": result.execution_time
        }
        
    except Exception as e:
        logger.error(f"Product recommendation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/project/analyze")
async def analyze_project(
    image: UploadFile = File(...),
    description: str = Form(None),
    project_type: str = Form("general"),
    budget_range: str = Form("medium"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Analyze a complete DIY project with multiple images"""
    
    try:
        logger.info(f"Starting project analysis - received image: {image.filename}")
        logger.info(f"Description: {description}, project_type: {project_type}")
    except Exception as e:
        logger.error(f"Error in initial logging: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing request: {str(e)}"
        )
    
    # Validate image
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File {image.filename} is not an image"
        )
    
    try:
        # Process image
        image_data = await image.read()
        images_data = [image_data]  # Put in list for agent compatibility
        
        logger.info(f"Processed image for project analysis: {len(image_data)} bytes")
        
        # Use dedicated project analysis agent
        project_result = await agent_manager.execute_task(
            "project_analysis",
            {
                "images": images_data,
                "description": description,
                "project_type": project_type,
                "budget_range": budget_range,
                "skill_level": "intermediate"
            }
        )
        
        if not project_result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=project_result.error or "Project analysis failed"
            )
        
        # Get tool identification for first image to add shopping links
        first_image = images_data[0]
        tool_result = await agent_manager.execute_task(
            "tool_identification",
            {
                "image_data": first_image,
                "include_alternatives": True
            }
        )
        
        # Combine comprehensive analysis with shopping links
        combined_result = project_result.data.copy()
        if tool_result.success:
            combined_result["tool_identification"] = tool_result.data
        
        # Add user context
        if current_user:
            combined_result["user_context"] = {
                "user_type": current_user.user_type,
                "personalized": True
            }
        
        return {
            "success": True,
            "data": combined_result,
            "execution_time": project_result.execution_time + (tool_result.execution_time if tool_result.success else 0)
        }
        
    except Exception as e:
        logger.error(f"Project analysis error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/user-product-recommendation/get")
async def get_user_product_recommendations(
    project_type: str = Form(...),
    budget_range: str = Form("50to150"),
    skill_level: str = Form("intermediate"),
    specific_needs: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get curated product recommendations for users with affiliate links"""
    
    try:
        # Parse specific needs if provided
        needs_list = specific_needs.split(",") if specific_needs else []
        
        # Add user preferences based on authentication
        user_preferences = {}
        if current_user:
            user_preferences = {
                "user_type": current_user.user_type,
                "personalized": True,
                "user_id": current_user.id
            }
        
        # Execute user product recommendation
        result = await agent_manager.execute_task(
            "user_product_recommendation",
            {
                "project_type": project_type,
                "budget_range": budget_range,
                "skill_level": skill_level,
                "specific_needs": [need.strip() for need in needs_list],
                "user_preferences": user_preferences
            }
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error or "Product recommendation failed"
            )
        
        # Add user context for personalization
        if current_user:
            result.data["user_context"] = {
                "user_type": current_user.user_type,
                "personalized": True,
                "recommendation_tier": "premium" if current_user.user_type in ["premium", "admin"] else "standard"
            }
            
            # Add special benefits for premium users
            if current_user.user_type == "premium":
                result.data["shopping_tips"].insert(0, "Premium members get exclusive early access to deals")
            elif current_user.user_type == "admin":
                result.data["shopping_tips"].insert(0, "Admin access: Manage product recommendations in admin panel")
        
        return {
            "success": True,
            "data": result.data,
            "execution_time": result.execution_time,
            "affiliate_notice": "This page contains affiliate links. We earn a commission from qualifying purchases at no extra cost to you."
        }
        
    except Exception as e:
        logger.error(f"User product recommendation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/status")
async def get_agents_status(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get status of all registered agents"""
    
    return {
        "agents": agent_manager.get_all_status(),
        "task_history": agent_manager.get_task_history(limit=10)
    }


@router.get("/available")
async def get_available_agents() -> Any:
    """Get list of available agents and their capabilities"""
    
    return {
        "agents": [
            {
                "name": "tool_identification",
                "description": "Identifies tools from images and finds shopping links",
                "endpoints": ["/api/v1/agents/tool-identification/analyze"],
                "requires_auth": False
            },
            {
                "name": "admin_product_analysis",
                "description": "Analyzes web product pages for admin database management",
                "endpoints": ["/api/v1/agents/admin-product-analysis/analyze"],
                "requires_auth": True,
                "admin_only": True
            },
            {
                "name": "project_analysis",
                "description": "Complete DIY project analysis with tools and recommendations",
                "endpoints": ["/api/v1/agents/project/analyze"],
                "requires_auth": False
            },
            {
                "name": "user_product_recommendation",
                "description": "Curated product recommendations with affiliate links for users",
                "endpoints": ["/api/v1/agents/user-product-recommendation/get"],
                "requires_auth": False,
                "features": ["affiliate_links", "budget_filtering", "personalization"]
            },
            {
                "name": "smart_tool_finder",
                "description": "Interactive conversational tool search and recommendation",
                "endpoints": ["/api/v1/agents/smart-tool-finder/chat"],
                "requires_auth": False,
                "features": ["conversation", "web_search", "filtering", "reasoning"]
            }
        ]
    }


# Pydantic models for Smart Tool Finder
from pydantic import BaseModel
from typing import Dict, List, Optional

class SmartToolFinderRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, str]] = {}
    conversation_history: Optional[List[Dict]] = []

@router.post("/smart-tool-finder/chat")
async def smart_tool_finder_chat(
    request: SmartToolFinderRequest,
    current_user: Optional[User] = Depends(get_optional_user)
) -> Any:
    """Process Smart Tool Finder conversational request"""
    
    try:
        logger.info(f"Smart Tool Finder chat request: {request.query}")
        
        # Prepare input data for the agent
        input_data = {
            "query": request.query,
            "filters": request.filters or {},
            "conversation_history": request.conversation_history or []
        }
        
        # Add user context if available
        if current_user:
            input_data["user_context"] = {
                "user_type": current_user.user_type,
                "username": current_user.username
            }
        
        # Execute the agent
        result = await smart_tool_finder_agent.execute(input_data)
        
        if not result.success:
            logger.error(f"Smart Tool Finder agent failed: {result.error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error or "Smart Tool Finder failed"
            )
        
        return {
            "success": True,
            "data": result.data,
            "execution_time": result.execution_time
        }
        
    except Exception as e:
        logger.error(f"Smart Tool Finder chat error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )