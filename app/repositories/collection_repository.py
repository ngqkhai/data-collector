from typing import List, Optional, Dict, Any
import os
from urllib.parse import urlparse
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId

from app.models.collection_model import Collection
from app.config import MONGO_URI

class CollectionRepository:
    """Repository for managing collections in MongoDB"""
    
    def __init__(self, mongo_uri: str = None):
        """Initialize repository with MongoDB connection"""
        self.mongo_uri = mongo_uri or MONGO_URI
        
        # Extract database name from URI or use default
        parsed_uri = urlparse(self.mongo_uri)
        db_name = parsed_uri.path.strip('/') or 'data_collector'
        
        # Connect to MongoDB
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[db_name]
        self.collections = self.db.collections
    
    def close(self):
        """Close MongoDB connection"""
        if hasattr(self, 'client') and self.client:
            self.client.close()
    
    def insert(self, collection: Collection) -> str:
        """Insert a new collection into the database"""
        result = self.collections.insert_one(collection.to_dict())
        return str(result.inserted_id)
    
    def find_by_id(self, collection_id: str) -> Optional[Collection]:
        """Find a collection by its ID"""
        try:
            document = self.collections.find_one({"_id": ObjectId(collection_id)})
            if document:
                return Collection.from_dict(document)
            return None
        except InvalidId:
            return None
    
    def find_all(self, limit: int = 100) -> List[Collection]:
        """Find all collections, with optional limit"""
        cursor = self.collections.find().sort("created_at", -1).limit(limit)
        return [Collection.from_dict(doc) for doc in cursor]
    
    def find_by_title(self, title: str) -> Optional[Collection]:
        """Find a collection by its title"""
        document = self.collections.find_one({"title": {"$regex": title, "$options": "i"}})
        if document:
            return Collection.from_dict(document)
        return None
    
    def update(self, collection_id: str, updates: Dict[str, Any]) -> bool:
        """Update a collection"""
        try:
            result = self.collections.update_one(
                {"_id": ObjectId(collection_id)},
                {"$set": updates}
            )
            return result.modified_count > 0
        except InvalidId:
            return False
    
    def delete(self, collection_id: str) -> bool:
        """Delete a collection"""
        try:
            result = self.collections.delete_one({"_id": ObjectId(collection_id)})
            return result.deleted_count > 0
        except InvalidId:
            return False