from typing import Dict, Any, Optional
from app.cleaners.wiki_cleaner import WikipediaCleaner
from app.cleaners.pubmed_cleaner import PubMedCleaner
from app.cleaners.base_cleaner import BaseCleaner

class CleanerFactory:
    """Factory to create appropriate cleaner instances based on data source"""
    
    @staticmethod
    def get_cleaner(source_type: str, file_type: Optional[str] = None) -> BaseCleaner:
        """Get the appropriate cleaner based on source type and file type
        
        Args:
            source_type: The type of data source (wikipedia, pubmed, file_upload, video_script)
            file_type: For file uploads, the file type (pdf, docx, txt)
            
        Returns:
            An appropriate cleaner instance
        """
        # Web source cleaners
        if source_type.lower() == "wikipedia":
            return WikipediaCleaner()
        elif source_type.lower() == "pubmed":
            return PubMedCleaner()
        
        # Default case
        else:
            return BaseCleaner()  # This will fail since BaseCleaner is abstract