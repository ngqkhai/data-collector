from typing import BinaryIO, Dict, Any
from app.providers.file.base_file_processor import FileContentProcessor
from app.utils.helpers import extract_topics

class TXTProcessor(FileContentProcessor):
    """Processor for TXT files"""
    
    def process_file(self, file: BinaryIO) -> Dict[str, Any]:
        """Extract text from TXT file"""
        try:
            # Try UTF-8 encoding first
            text = file.read().decode('utf-8')
        except UnicodeDecodeError:
            # If UTF-8 fails, try Latin-1 (should always work)
            file.seek(0)
            text = file.read().decode('latin-1')
        
        # Extract scientific topics
        scientific_topics = extract_topics(text)
        
        return {
            "content": text,
            "metadata": {
                "source": "file_upload",
                "file_type": "txt",
                "extraction_method": "plain-text",
                "scientific_topics": scientific_topics,
                "filename": getattr(file, 'filename', 'unknown.txt')
            }
        }