from abc import ABC, abstractmethod
from typing import List   
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_vertexai import VertexAIEmbeddings
from services.ai_clients import AIClientsSingleton
class ChunkingStrategy(ABC):
    """Abstract base class for all chunking strategies."""
    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        pass

class SemanticChunkingStrategy:
    """
    Semantic chunking + embedding generation in one step.
    Returns both chunks and their embeddings so they are ready for indexing.
    """
    def __init__(self):
        clients = AIClientsSingleton()
        self.embeddings = clients.embeddings_client
        self.text_splitter = clients.semantic_chunker

    def chunk_and_vectorize(self, text: str) -> List:
        """
        Splits text into semantic chunks and generates embeddings for each chunk.
        """

        documents = self.text_splitter.create_documents([text])
        chunks = [doc.page_content for doc in documents]

        return chunks
