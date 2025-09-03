# cleaning/cleaner.py

import re
from bs4 import BeautifulSoup

class Cleaner:
    """
    An advanced class for cleaning raw text, especially from academic papers
    or PDF extractions.
    """
    
    def _rejoin_hyphenated_words(self, text: str) -> str:
        """Joins words that have been split with a hyphen at the end of a line."""
        # Finds a word, a hyphen, a newline, and another word, then joins them.
        return re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    def _remove_preamble_and_references(self, text: str) -> str:
        """
        Tries to remove the initial title/author block and the final
        references/acknowledgements section.
        """
        # Remove the title, authors, abstract, keywords section
        # We split at "Introduction" and take everything after it.
        # This is an assumption that "Introduction" marks the start of the main content.
        parts = re.split(r'\n\s*1\.\s*Introduction\n', text, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) > 1:
            text = parts[1]

        # Remove the references, acknowledgements section at the end
        # We split at "Acknowledgements" or "References" and take everything before it.
        parts = re.split(r'\n\s*(Acknowledgements|References)\n', text, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) > 1:
            text = parts[0]
            
        return text

    def _remove_citations(self, text: str) -> str:
        """Removes in-text citations like [1], [22], or [23, 49-52]."""
        # This regex looks for patterns like [1], [2, 3], [4-7], [8, 10-12]
        return re.sub(r'\[\d+(,[\s\d-]+)*\]', '', text)

    def _remove_artifacts(self, text: str) -> str:
        """Removes other non-prose artifacts like figure captions, URLs, etc."""
        # Remove figure captions (e.g., "Figure 1. Some description.")
        text = re.sub(r'Figure \d+\..*?\n', '', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove any remaining garbled text (non-ASCII characters)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        return text

    def clean(self, text: str) -> str:
        """
        Applies a full, multi-stage cleaning pipeline to the text.
        """
        if not text:
            return ""

        # --- Cleaning Pipeline ---
        # The order of these steps is important.
        
        # 1. First, fix words that were broken by line breaks.
        cleaned_text = self._rejoin_hyphenated_words(text)

        # 2. Remove the large blocks of metadata at the start and end.
        cleaned_text = self._remove_preamble_and_references(cleaned_text)

        # 3. Remove in-text citations.
        cleaned_text = self._remove_citations(cleaned_text)
        
        # 4. Remove other artifacts like figure captions and URLs.
        cleaned_text = self._remove_artifacts(cleaned_text)

        # 5. Finally, normalize all remaining whitespace.
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

        return cleaned_text