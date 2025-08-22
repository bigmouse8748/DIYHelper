"""
API Module
"""

from fastapi import APIRouter

from .v1 import auth, users, health, agents, our_picks, test, admin

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(agents.router, prefix="/agents", tags=["AI Agents"])
api_router.include_router(our_picks.router, tags=["Our Picks"])
api_router.include_router(test.router, prefix="/test", tags=["Testing"])
api_router.include_router(admin.router, tags=["Admin"])

__all__ = ['api_router']