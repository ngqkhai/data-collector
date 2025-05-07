import re
from typing import Dict, Any
from .base_cleaner import BaseCleaner

class WikipediaCleaner(BaseCleaner):
    """Cleaner specifically for Wikipedia content"""
    
    def clean_specific(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean Wikipedia content by removing unwanted sections, citations, 
        and normalizing formatting
        """
        
        if "content" in data and isinstance(data["content"], str):
            data["content"] = self._clean_wikipedia_text(data["content"])
            
        return data
    
    def _clean_wikipedia_text(self, text: str) -> str:
        """
        Cleans Wikipedia content for AI processing by:
        1. Removing unwanted sections (references, links, etc.)
        2. Preserving mathematical formulas and structural elements
        3. Normalizing spacing and formatting
        4. Ensuring consistent header formatting
        
        Parameters:
        - text (str): Raw Wikipedia text
        
        Returns:
        - str: Cleaned text optimized for AI processing
        """
        # Early return for empty text
        if not text:
            return ""
        print("Cleaning Wikipedia text...")
        # Pre-clean: Fix malformed headers with trailing equals signs
        text = re.sub(r'(=={1,})\s*(.*?)\s*\1[\r\n]+=$', r'\1 \2 \1', text)
        
        # Normalize line endings to Unix style
        text = text.replace('\r\n', '\n')
            
        # STEP 1: Preserve important elements that need special handling
        preserved = {}
        preserve_count = 0
        
        # Helper function to preserve patterns
        def preserve(pattern):
            nonlocal preserve_count, text
            
            def replacer(match):
                nonlocal preserve_count
                key = f"||PRESERVED_{preserve_count}||"
                preserved[key] = match.group(0)
                preserve_count += 1
                return key
                
            return re.sub(pattern, replacer, text)
        
        # Preserve paragraph breaks, section headers and mathematical formulas
        text = text.replace("\n\n", "||PARA||")
        text = preserve(r'==(=*)\s*(.*?)\s*\1==')  # Section headers
        text = preserve(r'\{\\displaystyle[^}]+\}')  # Display math
        text = preserve(r'\$[^\$]+\$')  # Inline math
        
        # STEP 2: Remove unwanted sections - FIXED SECTION
        # First restore section headers for proper removal
        section_keys_to_restore = []
        for key, value in preserved.items():
            if '==' in value:  # Only restore section headers
                section_keys_to_restore.append(key)
        
        # Restore section headers but keep track of keys to not restore later
        section_keys_to_remove = []
        for key in section_keys_to_restore:
            text = text.replace(key, preserved[key])
            section_keys_to_remove.append(key)
        
        # Define unwanted sections with more flexible patterns
        unwanted_sections = [
            r"==\s*See also\s*==",
            r"==\s*References\s*==",
            r"==\s*Further reading\s*==",
            r"==\s*External links\s*==",
            r"==\s*Notes\s*=="
        ]
        
        # Improved section removal that handles various formatting scenarios
        for section in unwanted_sections:
            pattern = rf"({section}).*?(?===|\Z)"  # Match until next header or end of text
            text = re.sub(pattern, "", text, flags=re.DOTALL)
        
        # STEP 3: Remove citations and reference markers
        # (These complement the basic citation removals from WebCleaner)
        text = re.sub(r'\[\d+\]', '', text)  # [1], [2], etc.
        text = re.sub(r"\s*:\s*[\d§,–]+(?:\s*:\s*[\d§,–]+)*", "", text)  # : 123, : 45 : 67
        
        # STEP 4: Clean whitespace and normalize formatting
        text = re.sub(r"\s+", " ", text)  # Normalize spaces
        
        # Remove invisible Unicode characters
        invisible_chars = ["\u2061", "\u200b", "\u200c", "\u200d", "\u200e", "\u200f", "\ufeff"]
        for char in invisible_chars:
            text = text.replace(char, "")
        
        # STEP 5: Restore preserved elements
        text = text.replace("||PARA||", "\n\n")
        for key, value in preserved.items():
            if key not in section_keys_to_remove:  # Don't restore section headers we already handled
                text = text.replace(key, value)
        
        # STEP 6: Final formatting
        # Fix spacing around punctuation and parentheses
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        text = re.sub(r'\(\s+', '(', text)
        text = re.sub(r'\s+\)', ')', text)
        
        # Normalize section headers
        text = re.sub(r'(==+)\s*(.*?)\s*\1', r'\1 \2 \1', text)
        
        # Fix asymmetric headers
        text = re.sub(r'(={2,})\s*(.*?)\s*(={1,})', 
                      lambda m: f"{m.group(1)} {m.group(2)} {m.group(1)}" 
                      if len(m.group(3)) != len(m.group(1)) else m.group(0), 
                      text)
        
        # Fix malformed headers with trailing equals signs (after any preservation done)
        text = re.sub(r'(=={1,})\s*(.*?)\s*\1\s*\n\s*=', r'\1 \2 \1', text)
        
        # Ensure headers have proper spacing
        text = re.sub(r'(={2,}.*?={2,})([^\n])', r'\1\n\n\2', text)
        
        # Clean up any remaining standalone equal signs
        text = re.sub(r'(?<=\n)=(?=\s*\n)', '', text)
        
        # Normalize multiple newlines (max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _remove_wikipedia_specific(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove Wikipedia-specific elements like category links, edit links, etc."""
        if "content" in data and isinstance(data["content"], str):
            content = data["content"]
            
            # Remove category links
            content = re.sub(r'\[\[Category:.*?\]\]', '', content)
            
            # Remove language links
            content = re.sub(r'\[\[[a-z\-]+:[^\]]+\]\]', '', content)
            
            # Remove disambiguation notices
            content = re.sub(r'This article is about.*?For other uses.*?\n', '', content, flags=re.DOTALL)
            
            data["content"] = content
        return data

    def _clean_infobox(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and format Wikipedia infoboxes for better readability"""
        if "content" in data and isinstance(data["content"], str):
            content = data["content"]
            
            # Extract infobox data if needed
            infobox_pattern = r'\{\{Infobox.*?\}\}'
            infoboxes = re.findall(infobox_pattern, content, re.DOTALL)
            
            if infoboxes:
                # Store infobox data in a structured way if needed
                data["metadata"] = data.get("metadata", {})
                data["metadata"]["infobox"] = infoboxes[0]  # Store first infobox
                
                # Remove infoboxes from main content
                content = re.sub(infobox_pattern, '', content, flags=re.DOTALL)
                data["content"] = content
                
        return data
