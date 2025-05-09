from typing import BinaryIO, Dict, Any
from PyPDF2 import PdfReader
from app.providers.file.base_file_processor import FileContentProcessor
from app.utils.helpers import extract_topics
import io

class PDFProcessor(FileContentProcessor):
    """Processor for PDF files"""
    
    def process_file(self, file: BinaryIO) -> Dict[str, Any]:
        """Extract text from PDF file"""
        try:
            # Ensure we're at the start of the file
            if isinstance(file, io.BytesIO):
                file.seek(0)
            elif hasattr(file, 'file'):
                # For FastAPI UploadFile objects
                file = file.file
                file.seek(0)
            
            reader = PdfReader(file)
            text = ""
            metadata = {}
            
            # Extract text from pages
            for page in reader.pages:
                text += page.extract_text() or ""
                text += "\n"  # Add newline between pages
            
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
            
            return {
                "content": text,
                "metadata": {
                    **metadata,
                    "source": "file_upload",
                    "file_type": "pdf",
                    "extraction_method": "PyPDF2",
                    "filename": getattr(file, 'filename', 'unknown.pdf')
                }
            }
        except Exception as e:
            raise ValueError(f"Error processing PDF file: {str(e)}") 