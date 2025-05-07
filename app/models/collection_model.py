from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, validator

class CollectionCreate(BaseModel):
    """Schema for creating a collection"""
    title: str
    content: str
    url: Optional[str] = None
    scientific_topics: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "title": "DNA Structure",
                "content": "DNA is a double helix...",
                "url": "https://en.wikipedia.org/wiki/DNA",
                "scientific_topics": ["biology", "genetics"],
                "metadata": {"source": "wikipedia"}
            }
        }

class CollectionResponse(BaseModel):
    """Schema for collection response"""
    id: str
    title: str
    content: str
    url: Optional[str] = None
    scientific_topics: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60a3c3d6c2d93e3e1c6e9b2a",
                "title": "DNA Structure",
                "content": "DNA is a double helix...",
                "url": "https://en.wikipedia.org/wiki/DNA",
                "scientific_topics": ["biology", "genetics"],
                "metadata": {"source": "wikipedia"},
                "created_at": "2025-05-04T07:56:31"
            }
        }

class Collection:
    """Model representing a collection of content from various sources"""

    def __init__(self, title: str, content: str, scientific_topics: List[str] = None, 
                 metadata: Dict[str, Any] = None, url: Optional[str] = None, 
                 id: Optional[str] = None, created_at: Optional[datetime] = None):
        """Initialize a Collection instance"""
        self.id = id
        self.title = title
        self.content = content
        self.url = url
        self.scientific_topics = scientific_topics or []
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Collection to a dictionary for MongoDB storage"""
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "scientific_topics": self.scientific_topics,
            "metadata": self.metadata,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Collection':
        """Create a Collection from a MongoDB document"""
        id_str = str(data.pop('_id')) if '_id' in data else None
        return cls(id=id_str, **data)
    
    def __str__(self) -> str:
        """String representation of Collection"""
        return f"Collection(id={self.id}, title={self.title}, topics={len(self.scientific_topics)})"
    
    def to_response(self) -> CollectionResponse:
        """Convert to Pydantic response model"""
        return CollectionResponse(
            id=self.id,
            title=self.title,
            content=self.content,
            url=self.url,
            scientific_topics=self.scientific_topics,
            metadata=self.metadata,
            created_at=self.created_at
        )