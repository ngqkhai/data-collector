from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import aiofiles
import os
import tempfile
import shutil

from app.models.collection_model import CollectionResponse, CollectionCreate
from app.providers.collection_service import CollectionService

# Create router
router = APIRouter(tags=["collections"])

class ScriptSubmission(BaseModel):
    """Schema for script submission"""
    title: str
    content: str
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Quantum Computing Explained",
                "content": "In this video, we'll explore the principles of quantum computing..."
            }
        }

# Dependency
def get_collection_service():
    service = CollectionService()
    try:
        yield service
    finally:
        service.close()

@router.post("/collections/wikipedia", response_model=Dict[str, Any], status_code=201)
async def collect_from_wikipedia(
    data: Dict[str, str],
    service: CollectionService = Depends(get_collection_service)
):
    """Process a Wikipedia URL and create a collection"""
    url = data.get('url')
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    try:
        collection_id = service.process_url(url)
        return {
            "message": "Wikipedia article processed successfully",
            "collection_id": collection_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collections/upload-file", response_model=Dict[str, Any], status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    service: CollectionService = Depends(get_collection_service)
):
    """Upload and process a file"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            # Write the uploaded file content to the temporary file
            shutil.copyfileobj(file.file, temp)
            temp_path = temp.name
        
        # Process the file with the saved path
        with open(temp_path, "rb") as f:
            # Make sure the file object has a filename attribute
            f.filename = file.filename
            collection_id = service.process_file(f)
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        return {
            "message": "File processed successfully",
            "collection_id": collection_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/collections/script", response_model=Dict[str, Any], status_code=201)
async def submit_script(
    submission: ScriptSubmission,
    service: CollectionService = Depends(get_collection_service)
):
    """Submit a video script for processing"""
    try:
        collection_id = service.process_script(submission.content, submission.title)
        return {
            "message": "Video script processed successfully",
            "collection_id": collection_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections", response_model=Dict[str, List[CollectionResponse]])
async def get_all_collections(
    limit: int = Query(100, description="Maximum number of collections to return"),
    service: CollectionService = Depends(get_collection_service)
):
    """Get all collections"""
    collections = service.get_all_collections(limit)
    return {"collections": [c.to_response() for c in collections]}

@router.get("/collections/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: str,
    service: CollectionService = Depends(get_collection_service)
):
    """Get a collection by ID"""
    collection = service.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection not found: {collection_id}")
    
    return collection.to_response()

@router.delete("/collections/{collection_id}", response_model=Dict[str, str])
async def delete_collection(
    collection_id: str,
    service: CollectionService = Depends(get_collection_service)
):
    """Delete a collection by ID"""
    success = service.delete_collection(collection_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Collection not found: {collection_id}")
    
    return {"message": f"Collection {collection_id} deleted successfully"}

@router.get("/collections/{collection_id}/related", response_model=Dict[str, List[Dict[str, str]]])
async def get_related_articles(
    collection_id: str,
    service: CollectionService = Depends(get_collection_service)
):
    """Get related articles for a collection"""
    collection = service.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection not found: {collection_id}")
    
    related = service.get_related_articles(collection_id)
    return {"related_articles": related}