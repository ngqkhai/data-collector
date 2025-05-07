from typing import Dict, Any, Optional, List, BinaryIO
import os
import re

from app.models.collection_model import Collection
from app.repositories.collection_repository import CollectionRepository
from app.providers.url.wikipedia_processor import WikipediaProcessor
from app.providers.url.pubmed_processor import PubMedProcessor
from app.providers.file.pdf_processor import PDFProcessor
from app.providers.file.docx_processor import DOCXProcessor
from app.providers.file.txt_processor import TXTProcessor
from app.providers.script_processor import ScriptProcessor
from app.utils.helpers import is_wikipedia_url, get_file_extension
from app.cleaners.cleaner_factory import CleanerFactory
from datetime import datetime

class CollectionService:
    """Service for collecting data from various sources (Wikipedia, files, etc.)"""
    
    def __init__(self):
        """Initialize the service with its dependencies"""
        self.repository = CollectionRepository()
        
        # Initialize URL processors
        self.url_processors = {
            'wikipedia': WikipediaProcessor(),
            'pubmed': PubMedProcessor()
        }
        
        # Initialize file processors
        self.file_processors = {
            "pdf": PDFProcessor(),
            "docx": DOCXProcessor(),
            "txt": TXTProcessor()
        }
        
        # Initialize script processor
        self.script_processor = ScriptProcessor()
    
    def __enter__(self):
        """Support with statement"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close repository when used with with statement"""
        self.close()
    
    def close(self):
        """Close resources"""
        if hasattr(self, 'repository'):
            self.repository.close()
    
    def _get_url_processor(self, url: str):
        """Get appropriate processor for URL"""
        if is_wikipedia_url(url):
            return self.url_processors['wikipedia']
        
        if re.match(r'^https?://(www\.)?pubmed\.ncbi\.nlm\.nih\.gov/\d+', url):
            return self.url_processors['pubmed']
        
        raise ValueError("Unsupported URL type")
    
    def process_url(self, url: str) -> str:
        """Process URL and store as collection"""
        # Get appropriate processor for URL
        processor = self._get_url_processor(url)
        
        # Process the URL
        result = processor.process(url)
        content = result.get("content", "")
        metadata = result.get("metadata", {})
        title = metadata.get("title", "Article")
        
        # Get the source type for cleaning
        source_type = metadata.get("source", "web")
        
        # Clean the data before storage
        cleaner = CleanerFactory.get_cleaner(source_type)
        
        cleaned_data = cleaner.clean({
            "content": content,
            "metadata": metadata
        })
        # Add timestamp for when the content was collected and cleaned
        cleaned_data["metadata"]["collected_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") 
        
        # Create and store collection
        collection = Collection(
            title=title,
            content=cleaned_data["content"],
            url=url,
            scientific_topics=cleaned_data["metadata"].get("scientific_topics", []),
            metadata=cleaned_data["metadata"]
        )
        
        return self.repository.insert(collection)
    
    def process_file(self, file: BinaryIO) -> str:
        """Process an uploaded file and store as collection"""
        try:
            if not file or not hasattr(file, 'filename') or not file.filename:
                raise ValueError("Invalid file upload")
                
            # Get file extension
            filename = file.filename
            ext = get_file_extension(filename)
            
            if ext not in self.file_processors:
                supported_types = ", ".join(self.file_processors.keys())
                raise ValueError(f"Unsupported file type: {ext}. Supported types: {supported_types}")
            
            # Use the appropriate processor
            processor = self.file_processors[ext]
            result = processor.process(file)
            
            # Extract data from result
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            
            # Create a title from the filename or metadata
            title = metadata.get("title") if metadata.get("title") else os.path.splitext(filename)[0]
            
            # Clean the data before storage
            cleaner = CleanerFactory.get_cleaner("file_upload", ext)
            cleaned_data = cleaner.clean({
                "content": content,
                "metadata": metadata
            })
            
            # Extract scientific topics
            scientific_topics = cleaned_data["metadata"].get("scientific_topics", [])
            
            # Create and store the collection
            collection = Collection(
                title=title,
                content=cleaned_data["content"],
                url=None,  # This is a file, not a URL
                scientific_topics=scientific_topics,
                metadata=cleaned_data["metadata"]
            )
            
            return self.repository.insert(collection)
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            raise
    
    def process_script(self, script_content: str, title: str = "Video Script") -> str:
        """Process a video script and store as collection"""
        try:
            # Process the script
            result = self.script_processor.process(script_content)
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            
            # Clean the script data
            cleaner = CleanerFactory.get_cleaner("video_script")
            cleaned_data = cleaner.clean({
                "content": content,
                "metadata": metadata
            })
            
            # Extract scientific topics
            scientific_topics = cleaned_data["metadata"].get("scientific_topics", [])
            
            # Create and store the collection
            collection = Collection(
                title=title,
                content=cleaned_data["content"],
                url=None,
                scientific_topics=scientific_topics,
                metadata=cleaned_data["metadata"]
            )
            
            return self.repository.insert(collection)
            
        except Exception as e:
            print(f"Error processing script: {str(e)}")
            raise
    
    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Get a collection by ID"""
        return self.repository.find_by_id(collection_id)
    
    def get_all_collections(self, limit: int = 100) -> List[Collection]:
        """Get all collections"""
        return self.repository.find_all(limit)
    
    def find_by_title(self, title: str) -> Optional[Collection]:
        """Find a collection by title"""
        return self.repository.find_by_title(title)
    
    def delete_collection(self, collection_id: str) -> bool:
        """Delete a collection by ID"""
        return self.repository.delete(collection_id)
    
    def get_related_articles(self, collection_id: str) -> List[Dict[str, str]]:
        """Get related articles for a collection"""
        collection = self.get_collection(collection_id)
        if not collection:
            return []
            
        if collection.url and is_wikipedia_url(collection.url):
            return self.url_processors['wikipedia'].get_related_articles(collection.title)
        
        # For files or other content types, we might implement different related content logic
        # For now, return empty list for non-Wikipedia content
        return []