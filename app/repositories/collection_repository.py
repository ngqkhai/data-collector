import os
import logging
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.models.collection_model import Collection
from app.config import settings
import certifi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollectionRepository:
    def __init__(self):
        """Initialize MongoDB connection"""
        try:
            # Create client with SSL certificate verification
            self.client = AsyncIOMotorClient(
                settings.MONGO_URL,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000
            )
            self.db = self.client[settings.MONGO_DB]
            self.collection = self.db[settings.MONGO_COLLECTION]
            logger.info(f"Connected to MongoDB at {settings.MONGO_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")

    async def insert(self, collection: Collection) -> str:
        """Insert a new collection"""
        try:
            # Convert to dict and remove None values
            data = collection.model_dump(exclude_none=True)
            result = await self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting collection: {str(e)}")
            raise

    async def find_by_id(self, collection_id: str) -> Optional[Collection]:
        """Find a collection by ID"""
        try:
            if not ObjectId.is_valid(collection_id):
                return None
            result = await self.collection.find_one({"_id": ObjectId(collection_id)})
            if result:
                result["id"] = str(result.pop("_id"))
                return Collection(**result)
            return None
        except Exception as e:
            logger.error(f"Error finding collection: {str(e)}")
            raise

    async def find_by_title(self, title: str) -> Optional[Collection]:
        """Find a collection by title"""
        try:
            result = await self.collection.find_one({"title": title})
            if result:
                result["id"] = str(result.pop("_id"))
                return Collection(**result)
            return None
        except Exception as e:
            logger.error(f"Error finding collection by title: {str(e)}")
            raise

    async def find_all(self, limit: int = 100) -> List[Collection]:
        """Find all collections"""
        try:
            cursor = self.collection.find().limit(limit)
            collections = []
            async for doc in cursor:
                doc["id"] = str(doc.pop("_id"))
                collections.append(Collection(**doc))
            return collections
        except Exception as e:
            logger.error(f"Error finding all collections: {str(e)}")
            raise

    async def delete(self, collection_id: str) -> bool:
        """Delete a collection by ID"""
        try:
            if not ObjectId.is_valid(collection_id):
                return False
            result = await self.collection.delete_one({"_id": ObjectId(collection_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise