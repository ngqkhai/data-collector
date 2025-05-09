from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class CollectionCreate(BaseModel):
    """Schema for creating a collection"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "DNA Structure",
                "content": "DNA is a double helix...",
                "url": "https://en.wikipedia.org/wiki/DNA",
                "scientific_topics": ["biology", "genetics"],
                "metadata": {"source": "wikipedia"}
            }
        }
    )
    
    title: str
    content: str
    url: Optional[str] = None
    scientific_topics: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CollectionResponse(BaseModel):
    """Schema for collection response"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "60a3c3d6c2d93e3e1c6e9b2a",
                "title": "DNA Structure",
                "content": "DNA is a double helix...",
                "url": "https://en.wikipedia.org/wiki/DNA",
                "scientific_topics": ["biology", "genetics"],
                "metadata": {"source": "wikipedia"},
                "created_at": "2025-05-04T07:56:31",
                "updated_at": "2025-05-04T07:56:31"
            }
        }
    )
    
    id: str
    title: str
    content: str
    url: Optional[str] = None
    scientific_topics: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

class Collection(BaseModel):
    """Model for a collection of data"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Quantum Computing Basics",
                "content": "Quantum computing is a type of computing...",
                "url": "https://example.com/quantum-computing",
                "scientific_topics": ["quantum computing", "physics"],
                "metadata": {
                    "source": "wikipedia",
                    "language": "en"
                }
            }
        }
    )
    
    id: Optional[str] = None
    title: str
    content: str
    url: Optional[str] = None
    scientific_topics: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_response(self) -> CollectionResponse:
        """Convert to Pydantic response model"""
        return CollectionResponse(
            id=self.id or "",
            title=self.title,
            content=self.content,
            url=self.url,
            scientific_topics=self.scientific_topics,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=self.updated_at
        )