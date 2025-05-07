from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime

from app.repositories.collection_repository import CollectionRepository

# Create router
router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check() -> Dict[str, Any]:
        """Check the health status of the service and its dependencies
        
        Returns:
            Dictionary containing health information
        """
        # Check MongoDB connection
        mongo_status = "healthy"
        mongo_error = None
        
        try:
            # Create a temporary repository to check connection
            repo = CollectionRepository()
            # Try a simple MongoDB operation
            repo.collections.find_one({}, {"_id": 1})
            repo.close()
        except Exception as e:
            mongo_status = "unhealthy"
            mongo_error = str(e)
        
        # Generate response
        return {
            "status": "healthy" if mongo_status == "healthy" else "degraded",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0.0",  # This could be fetched from a config
            "dependencies": {
                "mongodb": {
                    "status": mongo_status,
                    "error": mongo_error
                }
            }
        }