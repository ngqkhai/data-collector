from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import aiofiles
import os
import tempfile
import shutil
import logging

from app.models.collection_model import CollectionResponse, CollectionCreate
from app.providers.collection_service import CollectionService
from app.repositories.collection_repository import CollectionRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["collections"])

class ScriptSubmission(BaseModel):
    """Schema for script submission"""
    title: Optional[str] = "User Script"
    content: str
    script_type: Optional[str] = None
    target_audience: Optional[str] = None
    duration: Optional[str] = None
    voice: Optional[str] = None
    language: Optional[str] = "en"
    visual_style: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Quantum Computing Explained",
                "content": "In this video, we'll explore the principles of quantum computing...",
                "script_type": "Explainer",
                "target_audience": "Students",
                "duration": "Medium",
                "voice": "Male Voice 1",
                "language": "en",
                "visual_style": "Minimal"
            }
        }

# Dependency
async def get_collection_service():
    repository = CollectionRepository()
    service = CollectionService(repository=repository)
    try:
        # Ensure message broker is connected
        await service.connect()
        logger.info("Message broker connected successfully")
        yield service
    except Exception as e:
        logger.error(f"Error connecting to message broker: {str(e)}")
        raise
    finally:
        # Only close the connection if it was successfully established
        if service._connected:
            await service.close()
            logger.info("Message broker connection closed")

@router.post("/api/collections/wikipedia", response_model=Dict[str, Any], status_code=201)
async def collect_from_wikipedia(
    data: Dict[str, str],
    service: CollectionService = Depends(get_collection_service)
):
    """Process a Wikipedia URL and create a collection"""
    url = data.get('url')
    script_params ={
        "script_type": data.get('script_type'),
        "target_audience": data.get('target_audience'),
        "duration": data.get('duration'),
        "voice": data.get('voice'),
        "language": data.get('language'),
        "visual_style": data.get('visual_style')
    }
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    try:
        logger.info(f"Processing Wikipedia URL: {url}")
        collection_id = await service.process_url(url, script_params)
        logger.info(f"Successfully processed Wikipedia URL. Collection ID: {collection_id}")
        return {
            "message": "Wikipedia article processed successfully",
            "collection_id": collection_id
        }
    except ValueError as e:
        logger.error(f"Invalid Wikipedia URL: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing Wikipedia URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/collections/upload-file", response_model=Dict[str, Any], status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    script_type: str = Form(...),
    target_audience: str = Form(...),
    duration: str = Form(...),
    language: str = Form("en"),
    visual_style: str = Form(...),
    voice: str = Form(...),
    service: CollectionService = Depends(get_collection_service)
):
    """Upload and process a file"""
    try:

        
        # Prepare configuration
        config = {
            "script_type": script_type,
            "target_audience": target_audience,
            "duration": duration,
            "language": language,
            "visual_style": visual_style,
            "voice": voice,
        }

        # Process file
        result = await service.process_file(file, config)
        return result

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/collections/script", response_model=Dict[str, Any], status_code=201)
async def submit_script(
    submission: ScriptSubmission,
    service: CollectionService = Depends(get_collection_service)
):
    """Submit a video script for processing"""
    try:
        # Create metadata from script parameters
        metadata = {
            "source": "user_input",
            "script_type": submission.script_type,
            "target_audience": submission.target_audience,
            "duration": submission.duration,
            "voice": submission.voice,
            "language": submission.language,
            "visual_style": submission.visual_style
        }
        
        collection_id = await service.process_script(
            content=submission.content, 
            title=submission.title,
            metadata=metadata
        )
        
        return {
            "message": "Video script processed successfully",
            "collection_id": collection_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing script: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/collections", response_model=Dict[str, List[CollectionResponse]])
async def get_all_collections(
    limit: int = Query(100, description="Maximum number of collections to return"),
    service: CollectionService = Depends(get_collection_service)
):
    """Get all collections"""
    collections = await service.get_all_collections(limit)
    return {"collections": [c.to_response() for c in collections]}

@router.get("/api/collections/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: str,
    service: CollectionService = Depends(get_collection_service)
):
    """Get a collection by ID"""
    collection = await service.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection not found: {collection_id}")
    
    return collection.to_response()

@router.delete("/api/collections/{collection_id}", response_model=Dict[str, str])
async def delete_collection(
    collection_id: str,
    service: CollectionService = Depends(get_collection_service)
):
    """Delete a collection by ID"""
    success = await service.delete_collection(collection_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Collection not found: {collection_id}")
    
    return {"message": f"Collection {collection_id} deleted successfully"}

@router.get("/api/collections/{collection_id}/related", response_model=Dict[str, List[Dict[str, str]]])
async def get_related_articles(
    collection_id: str,
    service: CollectionService = Depends(get_collection_service)
):
    """Get related articles for a collection"""
    collection = await service.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection not found: {collection_id}")
    
    related = await service.get_related_articles(collection_id)
    return {"related_articles": related}

@router.put("/api/collections/{collection_id}", response_model=Dict[str, Any])
async def update_collection(
    collection_id: str,
    data: Dict[str, Any],
    service: CollectionService = Depends(get_collection_service)
):
    """Update a collection by ID"""
    try:
        # Get existing collection
        collection = await service.get_collection(collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail=f"Collection not found: {collection_id}")
        
        # Update collection with new data
        updated_collection = Collection(
            id=collection_id,
            title=collection.title,  # Keep existing title
            content=data.get("content", collection.content),
            url=collection.url,  # Keep existing URL
            scientific_topics=collection.scientific_topics,  # Keep existing topics
            metadata={
                **collection.metadata,  # Keep existing metadata
                **data.get("metadata", {})  # Update with new metadata
            }
        )
        
        # Save updated collection
        success = await service.update_collection(updated_collection)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update collection")
        
        return {
            "message": "Collection updated successfully",
            "collection_id": collection_id
        }
    except Exception as e:
        logger.error(f"Error updating collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))