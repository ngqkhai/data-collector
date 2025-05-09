from typing import Dict, Any
from app.cleaners.base_cleaner import BaseCleaner

class FileCleaner(BaseCleaner):
    """Cleaner for uploaded files"""
    
    def __init__(self, file_type: str):
        """Initialize with file type
        
        Args:
            file_type: The type of file (pdf, docx, txt)
        """
        self.file_type = file_type
    
    def clean_specific(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean file content and metadata
        
        Args:
            data: The raw data dictionary containing content and metadata
            
        Returns:
            Cleaned data dictionary
        """
        content = data.get("content", "")
        metadata = data.get("metadata", {})
        
        # Basic text cleaning
        content = content.strip()
        
        # Add file-specific metadata
        metadata["file_type"] = self.file_type
        metadata["source"] = "file_upload"
        
        return {
            "content": content,
            "metadata": metadata
        } 