# cleaning/cleaner.py

import re
from bs4 import BeautifulSoup

class Cleaner:
    """
    A class dedicated to cleaning raw text content, especially from academic
    papers or PDF extractions.
    """
    
    def _remove_citations_and_footnotes(self, text: str) -> str:
        """Removes numbered footnotes and in-text citations."""
        # Removes patterns like "59 Internet and Educational..."
        # It looks for a number at the start of a line.
        text = re.sub(r'^\d+\s+.*$', '', text, flags=re.MULTILINE)
        
        # Removes inline citation numbers like if they exist
        text = re.sub(r'\\', '', text)
        return text

    def _remove_garbled_text(self, text: str) -> str:
        """Removes common garbled characters and patterns from bad encoding."""
        # This regex targets sequences of non-standard, often garbled characters
        # that you provided, like '£®\u009d\u009f¬'.
        # It looks for characters outside the    alphanumeric and punctuation range.
        # This can be adjusted to be more or less aggressive.
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        return text

    def _remove_headers_footers_and_artifacts(self, text: str) -> str:
        """Removes repetitive headers/footers and other artifacts."""
        # Removes lines that are just numbers (likely page numbers)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)

        # Example of removing a specific, repeating footer from your text.
        # You can add more patterns like this.
        footer_pattern = r'£®\u009d\u009f¬ ´²°\u009f´ ´£\u009a¦±¡.*©±¦£¨'
        text = re.sub(footer_pattern, '', text)
        
        # Removes URLs that might be part of the citations
        text = re.sub(r'http\S+|www\S+', '', text)
        
        return text

    def clean(self, text: str) -> str:
        """
        Applies a full cleaning pipeline to the text.
        
        Args:
            text (str): The raw text content.

        Returns:
            str: The cleaned text.
        """
        if not text:
            return ""

        # Apply the cleaning methods in a logical order
        cleaned_text = self._remove_citations_and_footnotes(text)
        cleaned_text = self._remove_headers_footers_and_artifacts(cleaned_text)
        cleaned_text = self._remove_garbled_text(cleaned_text)
        
        # Final whitespace normalization
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

        return cleaned_text