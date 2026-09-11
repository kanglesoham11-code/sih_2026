"""
ORCA Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.api import api_router
from app.live_api import router as live_router

# Setup logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title="ORCA API",
    description="Marine EcOsystem Reasoning with Collaborative Agents",
    version="1.0.0",
    docs_url="/docs" if settings.APP_ENV == "development" else None,
    redoc_url="/redoc" if settings.APP_ENV == "development" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(live_router)


@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("ORCA Marine Intelligence Platform starting...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1] if settings.DATABASE_URL else 'Not configured'}")
    
    # TODO: Initialize database connections
    # TODO: Run health checks on critical sources
    # TODO: Load source registry
    
    logger.info("ORCA startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("ORCA shutting down...")
    
    # TODO: Close database connections
    # TODO: Flush metrics
    
    logger.info("ORCA shutdown complete")


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "ORCA",
        "version": "1.0.0",
        "status": "operational",
        "description": "Marine EcOsystem Reasoning with Collaborative Agents",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_ENV == "development",
    )
