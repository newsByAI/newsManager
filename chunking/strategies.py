from abc import ABC, abstractmethod
from typing import List, Dict   
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_vertexai import VertexAIEmbeddings

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
    def __init__(self, project_id: str, location: str):
        # Embeddings client (reutilizado para chunking y vectorización final)
        self.embeddings = VertexAIEmbeddings(
            project=project_id,
            location=location,
            model_name="text-embedding-004"
        )
        # Semantic splitter (uses embeddings internally to cut text)
        self.text_splitter = SemanticChunker(
            self.embeddings, 
            breakpoint_threshold_type="percentile"
        )

    def chunk_and_vectorize(self, text: str) -> List:
        """
        Splits text into semantic chunks and generates embeddings for each chunk.
        
        Returns:
            List[Dict]: [{"chunk": str, "vector": List[float]}]
        """

        documents = self.text_splitter.create_documents([text])
        chunks = [doc.page_content for doc in documents]


        return chunks
