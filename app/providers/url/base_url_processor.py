from abc import abstractmethod
from typing import Dict, Any, List
import requests
from app.providers.base_content_processor import BaseContentProcessor

class BaseURLProcessor(BaseContentProcessor):
    """Base class for all URL content processors"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def process(self, url: str) -> Dict[str, Any]:
        """Process a URL and extract its content"""
        self.validate_url(url)
        return self.process_url(url)
    
    @abstractmethod
    def process_url(self, url: str) -> Dict[str, Any]:
        """Process the specific URL and extract content"""
        pass
    
    @abstractmethod
    def validate_url(self, url: str) -> None:
        """Validate that the URL is supported by this processor"""
        pass
    
    def fetch_url_content(self, url: str) -> str:
        """Fetch the content of a URL"""
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text