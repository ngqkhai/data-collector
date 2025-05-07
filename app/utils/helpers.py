import re
from typing import List, Optional
import os

def is_wikipedia_url(url: str) -> bool:
    """Check if a URL is a valid Wikipedia article URL"""
    pattern = r'^https?://(www\.)?([a-z]{2}\.)?wikipedia\.org/wiki/.+'
    return bool(re.match(pattern, url))

def get_file_extension(filename: str) -> str:
    """Get the file extension from a filename"""
    return os.path.splitext(filename)[1][1:].lower()

def is_supported_file_type(filename: str, supported_types: Optional[List[str]] = None) -> bool:
    """Check if a file type is supported"""
    if not supported_types:
        from app.config import SUPPORTED_FILE_TYPES
        supported_types = SUPPORTED_FILE_TYPES
    
    ext = get_file_extension(filename)
    return ext in supported_types

def extract_topics(text: str) -> List[str]:
    """Extract scientific topics from text
    
    This is a simple implementation that checks for keywords.
    In a production environment, consider using NLP techniques.
    """
    # Define scientific topics and their related keywords
    topics_dict = {
        "dna": ["dna", "genome", "genetic", "chromosome", "nucleotide", "gene"],
        "rna": ["rna", "mrna", "trna", "ribonucleic", "transcription"],
        "protein": ["protein", "amino acid", "peptide", "enzyme", "antibody"],
        "cell": ["cell", "cellular", "mitochondria", "nucleus", "organelle"],
        "biology": ["biology", "biological", "organism", "species", "taxonomy"],
        "physics": ["physics", "quantum", "relativity", "particle", "atomic"],
        "chemistry": ["chemistry", "chemical", "molecule", "compound", "reaction"],
        "math": ["math", "mathematics", "algorithm", "calculus", "equation"],
        "neuroscience": ["neuron", "brain", "neural", "synaptic", "cognitive"],
        "climate": ["climate", "atmospheric", "temperature", "greenhouse", "carbon"]
    }
    
    found_topics = set()
    text_lower = text.lower()
    
    for topic, keywords in topics_dict.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_topics.add(topic)
                break
    
    return list(found_topics)