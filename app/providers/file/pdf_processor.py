from typing import BinaryIO, Dict, Any
from PyPDF2 import PdfReader
from app.providers.file.base_file_processor import FileContentProcessor
from app.utils.helpers import extract_topics

class PDFProcessor(FileContentProcessor):
    """Processor for PDF files"""
    
    def process_file(self, file: BinaryIO) -> Dict[str, Any]:
        """Extract text from PDF file"""
        reader = PdfReader(file)
        text = ""
        metadata = {}
        
        # Extract text from pages
        for page in reader.pages:
            text += page.extract_text() or ""
        
        # Extract document information
        if reader.metadata:
            metadata = {
                "title": reader.metadata.get("/Title", ""),
                "author": reader.metadata.get("/Author", ""),
                "subject": reader.metadata.get("/Subject", ""),
                "creator": reader.metadata.get("/Creator", ""),
                "producer": reader.metadata.get("/Producer", ""),
                "page_count": len(reader.pages)
            }
        
        # Extract scientific topics
        scientific_topics = extract_topics(text)
        
        return {
            "content": text,
            "metadata": {
                **metadata,
                "source": "file_upload",
                "file_type": "pdf",
                "extraction_method": "PyPDF2",
                "scientific_topics": scientific_topics,
                "filename": getattr(file, 'filename', 'unknown.pdf')
            }
        }   