import re
from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
from app.providers.url.base_url_processor import BaseURLProcessor
from app.utils.helpers import extract_topics

class PubMedProcessor(BaseURLProcessor):
    """Processor for PubMed URLs"""
    
    def validate_url(self, url: str) -> None:
        """Validate that the URL is a PubMed article"""
        pattern = r'^https?://(www\.)?pubmed\.ncbi\.nlm\.nih\.gov/\d+'
        if not re.match(pattern, url):
            raise ValueError("The URL is not a valid PubMed article URL")
    
    def process_url(self, url: str) -> Dict[str, Any]:
        """Process a PubMed URL and extract its content"""
        try:
            # Fetch the HTML content
            html_content = self.fetch_url_content(url)
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = soup.find('h1', {'class': 'heading-title'}).text.strip()
            
            # Extract abstract
            abstract_div = soup.find('div', {'id': 'abstract'})
            if abstract_div:
                abstract = abstract_div.text.strip()
            else:
                abstract = "Abstract not available."
            
            # Extract authors
            authors_list = []
            authors_section = soup.find('div', {'class': 'authors-list'})
            if authors_section:
                authors = authors_section.find_all('span', {'class': 'authors-list-item'})
                for author in authors:
                    authors_list.append(author.text.strip())
            
            # Extract publication date
            pub_date = ""
            date_elem = soup.find('span', {'class': 'cit'})
            if date_elem:
                pub_date = date_elem.text.strip()
            
            # Extract scientific topics from content
            scientific_topics = extract_topics(abstract)
            
            # Extract DOI if available
            doi = ""
            doi_elem = soup.find('span', {'class': 'identifier doi'})
            if doi_elem:
                doi = doi_elem.text.strip().replace('doi: ', '')
            
            # Extract PMID
            pmid = re.search(r'/(\d+)/?$', url).group(1)
            
            # Extract metadata
            metadata = {
                "title": title,
                "url": url,
                "source": "pubmed",
                "pmid": pmid,
                "doi": doi,
                "authors": authors_list,
                "publication_date": pub_date,
                "scientific_topics": scientific_topics
            }
            
            return {
                "content": abstract,
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"Error processing PubMed URL: {e}")
            raise