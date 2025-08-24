"""
DIY Smart Assistant - Main Application
FastAPI application with JWT authentication
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from .config import settings
from .database import create_tables
from .api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="智能DIY助手平台 - AI驱动的项目分析和工具识别",
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add logging middleware first (will execute last)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"{response.status_code} - {process_time:.3f}s"
    )
    
    return response

# Trusted hosts (for production) - Make sure to allow proper hosts
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["api.cheasydiy.com", "cheasydiy.com", "www.cheasydiy.com", "localhost", "127.0.0.1"]
    )

# CORS middleware - Environment-aware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parse_cors_origins(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    
    # Get origin from request headers for CORS
    origin = request.headers.get("origin")
    headers = {}
    
    # Add CORS headers if origin is allowed
    allowed_origins = [
        "https://cheasydiy.com",
        "https://www.cheasydiy.com",
        "https://api.cheasydiy.com",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost:8082",
        "http://localhost:8083",
        "http://localhost:8084",
        "http://localhost:8085",
        "http://localhost:8086",
        "http://localhost:8087",
        "http://localhost:8088",
        "http://127.0.0.1:8088",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
    ]
    
    if origin in allowed_origins:
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later."
        },
        headers=headers
    )


@app.on_event("startup")
async def startup():
    """Application startup event"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # 自动同步数据库schema
    try:
        from .sync_database_schema import sync_database_schema
        await sync_database_schema()
        logger.info("Database schema synchronized successfully")
    except Exception as e:
        logger.error(f"Database schema synchronization failed: {e}")
        # 回退到基本的表创建
        try:
            await create_tables()
            logger.info("Fallback: Database tables created/verified successfully")
        except Exception as fallback_error:
            logger.error(f"Database initialization completely failed: {fallback_error}")
            # Continue startup anyway - tables might already exist
    
    logger.info("Application started successfully")

# Include API router
app.include_router(api_router)


@app.on_event("shutdown")
async def shutdown():
    """Application shutdown event"""
    logger.info("Shutting down application")


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "timestamp": time.time()
    }

@app.get("/api/test")
async def api_test(request: Request):
    """API test endpoint for ALB health checks"""
    try:
        return {
            "status": "ok", 
            "message": "API is working",
            "timestamp": time.time(),
            "host": request.headers.get("host", "unknown"),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "method": request.method,
            "url": str(request.url)
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": time.time()
        }

# 添加更简单的健康检查端点作为备选
@app.get("/health")
async def health_simple():
    """Simplified health check"""
    return {"status": "ok"}

@app.get("/api/v1/health/status") 
async def health_detailed():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "timestamp": time.time()
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Documentation not available in production",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )