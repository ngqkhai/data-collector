from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseContentProcessor(ABC):
    """Abstract base class for all content processors"""
    
    @abstractmethod
    def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Process the input data and return extracted content
        
        Args:
            input_data: The input data to process (URL, file, etc.)
            
        Returns:
            Dictionary containing the processed content and metadata
        """
        pass