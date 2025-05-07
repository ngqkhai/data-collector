from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime


class BaseCleaner(ABC):
    """Base class for all data cleaners"""
    
    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean the collected data before storage
        
        Args:
            data: The raw data dictionary containing content and metadata
            
        Returns:
            Cleaned data dictionary
        """
        # Common cleaning tasks for all data types
        
        # Run the specific cleaning tasks for this data type
        data = self.clean_specific(data)
        
        # Add cleaning metadata
        data["metadata"] = data.get("metadata", {})
        data["metadata"]["cleaned"] = True
        data["metadata"]["cleaned_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        return data
    
    @abstractmethod
    def clean_specific(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement specific cleaning logic for each data type"""
        pass