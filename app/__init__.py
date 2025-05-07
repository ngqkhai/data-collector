from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from app.routes.collection_routes import router as collection_router
from app.routes.health_routes import router as health_router

def create_app():
    """Create and configure FastAPI application"""
    # Create FastAPI application
    app = FastAPI(
        title="Data Collector API",
        description="API for collecting data from various sources",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(collection_router, prefix="/api")
    app.include_router(health_router)  # Health router at root level
    
    # Add exception handlers
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle any unhandled exceptions"""
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)}
        )
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Welcome to Data Collector API",
            "docs_url": "/docs",
            "health_url": "/health"
        }
    
    return app