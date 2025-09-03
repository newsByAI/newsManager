from abc import ABC, abstractmethod
from typing import List
from ingestion.models import Article

# --- Interface (The Adapter Contract) ---
class NewsProvider(ABC):
    """Interface that all news providers must implement."""
    @abstractmethod
    def fetch_articles(self, query: str) -> List[Article]:
        pass



