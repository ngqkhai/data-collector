from typing import Dict, Any, Optional
from app.cleaners.wiki_cleaner import WikipediaCleaner
from app.cleaners.pubmed_cleaner import PubMedCleaner
from app.cleaners.file_cleaner import FileCleaner
from app.cleaners.base_cleaner import BaseCleaner

class CleanerFactory:
    """Factory to create appropriate cleaner instances based on data source"""
    
    @staticmethod
    def get_cleaner(source_type: str, file_type: Optional[str] = None) -> BaseCleaner:
        """Get the appropriate cleaner based on source type
        
        Args:
            source_type: The type of data source (wikipedia, pubmed)
            file_type: Not used, kept for backward compatibility
            
        Returns:
            An appropriate cleaner instance
        """
        # Web source cleaners
        if source_type.lower() == "wikipedia":
            return WikipediaCleaner()
        elif source_type.lower() == "pubmed":
            return PubMedCleaner()
        elif source_type.lower() == "file_upload":
            if not file_type:
                raise ValueError("File type is required for file uploads")
            return FileCleaner(file_type)
        
        # Default case
        raise ValueError(f"Unsupported source type: {source_type}")