import requests
from typing import Dict, Any, Optional


class ServiceClient:
    """Simple HTTP client for communicating with other services"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    def get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make a GET request to another service"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make a POST request to another service"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()