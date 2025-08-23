"""
Test endpoints for Our Picks functionality without authentication
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import Response
import logging

from ...agents.product_info_agent import ProductInfoAgent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.options("/our-picks/analyze")
async def analyze_options():
    """Handle OPTIONS request for test analyze endpoint"""
    return Response(status_code=200)


@router.post("/our-picks/analyze")
async def test_analyze_product(
    product_url: str = Form(...)
) -> Dict[str, Any]:
    """Test endpoint to analyze product URL without authentication"""
    try:
        agent = ProductInfoAgent()
        
        result = await agent.execute({
            "product_url": product_url,
            "task_type": "product_analysis"
        })
        
        if result.success:
            return {
                "success": True,
                "product": result.data,
                "message": "Product analysis completed successfully"
            }
        else:
            return {
                "success": False,
                "error": result.error,
                "message": "Product analysis failed"
            }
            
    except Exception as e:
        logger.error(f"Test analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/our-picks/status")
async def test_status() -> Dict[str, Any]:
    """Test endpoint to check Our Picks service status"""
    return {
        "success": True,
        "message": "Our Picks test service is running",
        "endpoints": {
            "analyze": "/api/v1/test/our-picks/analyze",
            "status": "/api/v1/test/our-picks/status"
        },
        "note": "This is a test endpoint that bypasses authentication for development"
    }