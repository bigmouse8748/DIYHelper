"""
Health check API endpoints
"""

from typing import Any
from fastapi import APIRouter
import time

from ...config import settings

router = APIRouter()


@router.get("/status")
async def health_status() -> Any:
    """Get health status"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "timestamp": time.time()
    }


@router.get("/ready")
async def readiness_check() -> Any:
    """Readiness check for deployment"""
    # TODO: Add database connection check
    # TODO: Add external service checks
    return {
        "ready": True,
        "checks": {
            "database": True,
            "cache": True
        }
    }