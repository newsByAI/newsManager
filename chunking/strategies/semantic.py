from services.ai_clients import AIClientsSingleton    
from strategies.strategy_i import ChunkingStrategy
from typing import List

class SemanticChunkingStrategy(ChunkingStrategy):
    """
    Semantic chunking + embedding generation in one step.
    Returns both chunks and their embeddings so they are ready for indexing.
    """
    def __init__(self):
        clients = AIClientsSingleton()
        self.embeddings = clients.embeddings_client
        self.text_splitter = clients.semantic_chunker

    def chunk(self, text: str) -> List[str]:
        """
        Splits text into semantic chunks.
        """
        documents = self.text_splitter.create_documents([text])
        return [doc.page_content for doc in documents]

