import re
from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from app.providers.url.base_url_processor import BaseURLProcessor
from app.utils.helpers import extract_topics

class WikipediaProcessor(BaseURLProcessor):
    """Processor for Wikipedia URLs"""
    
    def validate_url(self, url: str) -> None:
        """Validate that the URL is a Wikipedia article"""
        pattern = r'^https?://(www\.)?([a-z]{2}\.)?wikipedia\.org/wiki/.+'
        if not re.match(pattern, url):
            raise ValueError("The URL is not a valid Wikipedia article URL")
    
    def process_url(self, url: str) -> Dict[str, Any]:
        """Process a Wikipedia URL and extract its content"""
        try:
            # Extract title from URL
            title = self._extract_title_from_url(url)
            language = self._detect_language(url)
            
            # Fetch full article text using Wikipedia API
            content = self._fetch_full_article_text(title, language)
            
            # If API fails, fall back to HTML parsing
            if not content:
                html_content = self.fetch_url_content(url)
                content = self._extract_content_from_html(html_content)
            
            # Extract scientific topics from content
            scientific_topics = extract_topics(content)
            
            # Extract metadata
            metadata = {
                "title": title,
                "url": url,
                "source": "wikipedia",
                "language": language,
                "scientific_topics": scientific_topics
            }
            
            return {
                "content": content,
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"Error processing Wikipedia URL: {e}")
            raise
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract the article title from a Wikipedia URL"""
        # Extract the path component after /wiki/
        match = re.search(r'/wiki/([^?#]+)', url)
        if match:
            # URL decode the title (replace underscores with spaces)
            encoded_title = match.group(1)
            title = unquote(encoded_title).replace('_', ' ')
            return title
        
        # Fallback: fetch the HTML and extract the title
        html_content = self.fetch_url_content(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        title_elem = soup.find('h1', {'id': 'firstHeading'})
        if title_elem:
            return title_elem.text
        
        raise ValueError("Could not extract title from Wikipedia URL")
    
    def _fetch_full_article_text(self, title: str, language: str = "en") -> str:
        """Fetch full Wikipedia article text, handling pagination if necessary.
        
        Args:
            title: The title of the Wikipedia article
            language: The language code (e.g., "en", "fr")
            
        Returns:
            The full article text as a string
        """
        base_url = f"https://{language}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "explaintext": True,
            "titles": title,
            "formatversion": "2"
        }
        
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            # Extract text from the response
            if "query" in data and "pages" in data["query"]:
                page = data["query"]["pages"][0]
                if "extract" in page:
                    
                    return page["extract"]
            
            return ""
        except Exception as e:
            print(f"Error fetching article text via API: {e}")
            return ""
    
    def _extract_content_from_html(self, html_content: str) -> str:
        """Extract article content from HTML (fallback method)"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the main content div
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            return ""
        
        # Extract all paragraphs
        paragraphs = content_div.find_all('p')
        
        # Concatenate paragraphs into a single text
        content = '\n\n'.join([p.text for p in paragraphs if p.text.strip()])
        
        return content
    
    def get_related_articles(self, title: str) -> List[Dict[str, str]]:
        """Get related articles for a Wikipedia title"""
        try:
            # Construct URL for Wikipedia API
            api_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={title}&format=json&utf8=1&srlimit=5"
            
            # Fetch data from API
            response = requests.get(api_url, headers=self.headers)
            data = response.json()
            
            # Extract search results
            results = data.get('query', {}).get('search', [])
            
            # Format results
            related_articles = []
            for result in results:
                # Skip the same article
                if result['title'].lower() == title.lower():
                    continue
                    
                article_url = f"https://en.wikipedia.org/wiki/{result['title'].replace(' ', '_')}"
                related_articles.append({
                    "title": result['title'],
                    "url": article_url,
                    "snippet": BeautifulSoup(result.get('snippet', ''), 'html.parser').text
                })
                
            return related_articles
            
        except Exception as e:
            print(f"Error getting related articles: {e}")
            return []
    
    def _detect_language(self, url: str) -> str:
        """Detect language from Wikipedia URL"""
        match = re.match(r'^https?://([a-z]{2})\.wikipedia\.org/wiki/', url)
        if match:
            return match.group(1)
        return "en"  # Default to English