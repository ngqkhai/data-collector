from typing import Dict, Any, Optional, List, BinaryIO
import os
import re
import asyncio
import logging
from fastapi import UploadFile

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
from app.providers.message_broker import DataCollectorMessageBroker

logger = logging.getLogger(__name__)

class CollectionService:
    """Service for collecting data from various sources (Wikipedia, files, etc.)"""
    
    def __init__(self, repository: CollectionRepository):
        """Initialize the service with its dependencies"""
        self.repository = repository
        self.message_broker = DataCollectorMessageBroker()
        self._connected = False
        
        # Initialize URL processors
        self.url_processors = {
            'wikipedia': WikipediaProcessor(),
            'pubmed': PubMedProcessor()
        }
        
        # Initialize file processors
        self.file_processors = {
            '.pdf': PDFProcessor(),
            '.docx': DOCXProcessor(),
            '.txt': TXTProcessor()
        }
        
        # Initialize script processor
        self.script_processor = ScriptProcessor()
        
        self.pdf_processor = PDFProcessor()
        self.txt_processor = TXTProcessor()
        self.docx_processor = DOCXProcessor()
        self.url_processor = {
            'wikipedia': WikipediaProcessor(),
            'pubmed': PubMedProcessor()
        }
    
    async def __aenter__(self):
        """Support async with statement"""
        await self.ensure_connected()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close repository when used with async with statement"""
        await self.close()
    
    async def close(self):
        """Close all resources"""
        # Close repository synchronously
        if hasattr(self, 'repository'):
            self.repository.close()
        # Close message broker asynchronously
        if hasattr(self, 'message_broker'):
            await self.message_broker.close()
    
    def _get_url_processor(self, url: str):
        """Get appropriate processor for URL"""
        if is_wikipedia_url(url):
            return self.url_processors['wikipedia']
        
        if re.match(r'^https?://(www\.)?pubmed\.ncbi\.nlm\.nih\.gov/\d+', url):
            return self.url_processors['pubmed']
        
        raise ValueError("Unsupported URL type")
    
    async def process_url(self, url: str, script_params: Dict[str, Any] = None) -> str:
        """Process URL and store as collection"""
        try:
            # Ensure message broker is connected
            await self.ensure_connected()
            logger.info("Message broker connection verified")
            
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
            
            collection_id = await self.repository.insert(collection)
            logger.info(f"Collection stored with ID: {collection_id}")
            
            # Default script parameters if none provided
            default_params = {
                "script_type": "educational",
                "target_audience": "General Public",
                "duration": 300,
                "language": "en"
            }
            
            # Merge default parameters with provided parameters
            script_params = {**default_params, **(script_params or {})}
            logger.info(f"Script parameters: {script_params}")
            # Publish to message broker
            message_data = {
                "content": cleaned_data["content"],
                "metadata": cleaned_data["metadata"],
                "collection_id": collection_id,
                "source_type": "url",
                "source_name": url,
                **script_params  # Include all script generation parameters
            }
            logger.info(message_data)
            logger.info("Publishing message to broker...")
            await self.message_broker.publish_data_collected(message_data)
            logger.info("Message published successfully")
            
            return collection_id
            
        except Exception as e:
            logger.error(f"Error processing URL: {str(e)}")
            raise
    
    async def process_file(self, file: UploadFile, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process uploaded file and publish to message broker"""
        try:
            # Ensure message broker connection
            await self.ensure_connected()
            if not file or not hasattr(file, 'filename') or not file.filename:
                raise ValueError("Invalid file upload")
            
            # Get file extension
            filename = file.filename
            ext = "." + get_file_extension(filename)
            if ext not in self.file_processors:
                supported_types = ", ".join(self.file_processors.keys())
                raise ValueError(f"Unsupported file type: {ext}. Supported types: {supported_types}")
            
            logger.info(f"Processing file: {file.filename} with config: {config}")
            
             # Use the appropriate processor
            processor = self.file_processors[ext]
            result = processor.process(file)
                
            # Create message data
            message_data = {
                "content": result["content"],
                "filename": file.filename,
                "content_type": file.content_type,
                "source_type": "file_upload",
                "collection_id": None  # Will be set after DB insert
            }
                
            # Add all config fields to message data
            message_data.update(config)
                
            # Create a collection object
            collection = Collection(
                title=f"File: {file.filename}",
                content=result["content"],
                url=None,
                scientific_topics=[],
                metadata={
                    "source": "file_upload",
                    "filename": file.filename,
                    "content_type": file.content_type,
                **config
            }
            )
                
                # Save to database
            collection_id = await self.repository.insert(collection)
            message_data["collection_id"] = collection_id

            # Publish to message broker
            logger.info(f"Publishing file data to message broker, collection_id: {collection_id}")
            await self.message_broker.publish_data_collected(message_data)
            logger.info("File data published successfully")

            return {
                "status": "success",
                "message": "File processed and published successfully",
                    "collection_id": collection_id
            }

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            raise
    
    async def process_script(self, content: str, title: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a submitted script and create a collection
        
        Args:
            content: The script content
            title: The title of the script
            metadata: Optional metadata about the script
            
        Returns:
            The ID of the created collection
        """
        try:
            # Ensure connection to message broker
            await self.ensure_connected()
            
            # Create collection object
            collection = Collection(
                title=title,
                content=content,
                scientific_topics=[],  # No topics for direct script submission
                **metadata # Use provided metadata or empty dict
            )
            
            # Save collection to database
            collection_id = await self.repository.insert(collection)
            logger.info(f"Script collection created with ID: {collection_id}")
            
            # Prepare message data for processing queue
            message_data = {
                "content": content,
                "collection_id": collection_id,
                "source_type": "user_script",
                "title": title
            }
            
            # Add metadata fields directly to message data
            if metadata:
                for key, value in metadata.items():
                    if key not in message_data:  # Avoid overwriting existing fields
                        message_data[key] = value
            
            # Publish to processing queue
            logger.info(f"Publishing script collection to queue: {collection_id}")
            logger.info(f"Message data: {message_data}")
            await self.message_broker.publish_data_collected(message_data)
            logger.info(f"Script collection published successfully: {collection_id}")
            
            return str(collection_id)
        except Exception as e:
            logger.error(f"Error processing script: {str(e)}")
            raise
    
    async def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Get a collection by ID"""
        return await self.repository.find_by_id(collection_id)
    
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

    async def connect(self):
        """Connect to message broker"""
        await self.message_broker.connect()
        self._connected = True

    async def ensure_connected(self):
        """Ensure message broker is connected"""
        if not self._connected:
            await self.connect()

    async def update_collection(self, collection: Collection) -> bool:
        """Update a collection in the database"""
        try:
            return await self.repository.update(collection)
        except Exception as e:
            logger.error(f"Error updating collection: {str(e)}")
            raise