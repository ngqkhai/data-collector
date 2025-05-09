from typing import BinaryIO, Dict, Any
from app.providers.file.base_file_processor import FileContentProcessor
from app.utils.helpers import extract_topics

class TXTProcessor(FileContentProcessor):
    """Processor for TXT files"""
    
    def process_file(self, file: BinaryIO) -> Dict[str, Any]:
        """Extract text from TXT file"""
        try:
            # Handle FastAPI UploadFile objects
            if hasattr(file, 'file'):
                file_obj = file.file
                # Store filename for later use
                filename = getattr(file, 'filename', 'unknown.txt')
            else:
                file_obj = file
                filename = getattr(file, 'filename', 'unknown.txt')
                
            # Try UTF-8 encoding first
            file_obj.seek(0)
            text = file_obj.read().decode('utf-8')
        except UnicodeDecodeError:
            # If UTF-8 fails, try Latin-1 (should always work)
            file_obj.seek(0)
            text = file_obj.read().decode('latin-1')
        
        
        return {
            "content": text,
            "metadata": {
                "source": "file_upload",
                "file_type": "txt",
                "extraction_method": "plain-text",
                "filename": filename
            }
        }