from typing import Dict, Any
from app.providers.base_content_processor import BaseContentProcessor
from app.utils.helpers import extract_topics

class ScriptProcessor(BaseContentProcessor):
    """Processor for video script content"""
    
    def process(self, input_data: str) -> Dict[str, Any]:
        """Process a video script content
        
        Args:
            input_data: The script text content
            
        Returns:
            Dictionary containing the processed content and metadata
        """
        if not isinstance(input_data, str):
            raise TypeError("Input must be a string containing script content")
        
        # Extract scientific topics from the script content
        scientific_topics = extract_topics(input_data)
        
        # Basic script analysis
        lines = input_data.split('\n')
        word_count = len(input_data.split())
        
        return {
            "content": input_data,
            "metadata": {
                "source": "video_script",
                "line_count": len(lines),
                "word_count": word_count,
                "scientific_topics": scientific_topics
            }
        }