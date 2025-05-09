from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import sys

from app.routes.collection_routes import router as collection_router
from app.routes.health_routes import router as health_router
from app.providers.collection_service import CollectionService
from app.repositories.collection_repository import CollectionRepository
from app.providers.message_broker import DataCollectorMessageBroker
from app.config import settings

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('data_collector.log')
    ]
)

logger = logging.getLogger(__name__)

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
    
    # Initialize repository and service
    repository = CollectionRepository()
    collection_service = CollectionService(repository=repository)
    
    # Include routers
    app.include_router(collection_router, tags=["collections"])
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
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup"""
        try:
            await collection_service.connect()
            logger.info("Services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize services: {str(e)}")
            raise
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        try:
            await collection_service.close()
            logger.info("Services cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    return app