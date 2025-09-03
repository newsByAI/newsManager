from typing import List
from .strategies.strategy_i import ChunkingStrategy
from ingestion.models import Article

class DocumentChunker:
    """
    Context class that uses a chunking strategy to split a document.
    """
    def __init__(self, strategy: ChunkingStrategy):
        self._strategy = strategy

    def chunk(self, article: Article) -> List[str]:
        """
        Chunks the content of an article using the configured strategy.
        """
        return self._strategy.chunk(article.content)