from abc import abstractmethod
from typing import BinaryIO, Dict, Any
from app.providers.base_content_processor import BaseContentProcessor

class FileContentProcessor(BaseContentProcessor):
    """Base class for all file content processors"""
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB default
    
    def process(self, input_data: BinaryIO) -> Dict[str, Any]:
        """Main processing method implementing BaseContentProcessor interface"""
        self.validate_file(input_data)
        return self.process_file(input_data)
    
    def validate_file(self, file: BinaryIO) -> None:
        """Common validation for all file types"""
        # Check if file is empty
        file.seek(0, 2)  # Go to end of file
        size = file.tell()  # Get position (size)
        file.seek(0)  # Reset position to beginning
        
        if size == 0:
            raise ValueError("File is empty")
        
        if size > self.max_file_size:
            raise ValueError(f"File exceeds maximum size of {self.max_file_size / (1024 * 1024)}MB")
    
    @abstractmethod
    def process_file(self, file: BinaryIO) -> Dict[str, Any]:
        """Process the specific file type and extract content"""
        pass