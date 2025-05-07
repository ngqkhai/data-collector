import re
from typing import Dict, Any
from .base_cleaner import BaseCleaner

class PubMedCleaner(BaseCleaner):
    """Specific cleaner for PubMed content"""
    
    def clean_specific(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean PubMed-specific content"""
        # First apply web cleaner
        data = super().clean_specific(data)
        
        # Then apply PubMed-specific cleaning
        data = self._structure_abstract(data)
        data = self._clean_medical_artifacts(data)
        return data
    
    def _structure_abstract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure the abstract into sections if applicable"""
        if "content" in data and isinstance(data["content"], str):
            content = data["content"]
            
            # Identify and format abstract sections
            section_patterns = [
                r'(BACKGROUND|INTRODUCTION):', 
                r'(METHODS|MATERIALS AND METHODS):', 
                r'(RESULTS):', 
                r'(CONCLUSION|CONCLUSIONS|DISCUSSION):'
            ]
            
            # Ensure sections are properly formatted
            for pattern in section_patterns:
                content = re.sub(pattern, r'\n\n\1:\n', content, flags=re.IGNORECASE)
                
            data["content"] = content
        return data
    
    def _clean_medical_artifacts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean PubMed-specific medical artifacts"""
        if "content" in data and isinstance(data["content"], str):
            content = data["content"]
            
            # Standardize medical abbreviations
            medical_abbr = {
                r'\bRCT\b': 'Randomized Controlled Trial',
                r'\bDOI\b': 'Digital Object Identifier',
                r'\bPMID\b': 'PubMed ID'
            }
            
            for abbr, full in medical_abbr.items():
                # Only expand the first occurrence, leave others as is
                content = re.sub(abbr, full, content, count=1, flags=re.IGNORECASE)
                
            data["content"] = content
        return data