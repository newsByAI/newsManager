import logging
from storage.vector_store import VectorStore

logger = logging.getLogger(__name__)


class SearchError(Exception):
    """Custom exception for search failures."""


class SearchService:
    def __init__(self):
        self.vector_store = VectorStore()

    def search_articles(self, query: str, k: int = 10):
        if not query or not query.strip():
            msg = "Search query cannot be empty."
            logger.warning(msg)
            raise SearchError(msg)

        try:
            results = self.vector_store.search_similar(query, k=k)
            if not results:
                logger.info(f"No results found for query: '{query}'")
                return []
            return results
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}", exc_info=True)
            raise SearchError("Semantic search failed") from e
