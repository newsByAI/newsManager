from typing import List, Dict
from services.vector_store_client import VectorStoreSingleton


class VectorStore:
    """
    Manage vectorization and storage in Vertex AI Search.
    """

    def __init__(self):
        self.client = VectorStoreSingleton()
        self.embeddings = self.client.embeddings
        self.index = self.client.index

    def vectorize_and_store(self, article_id: int, chunks: List[str]) -> List[Dict]:
        """
        Generates embeddings for the given chunks and stores them in Vertex AI Search.
        """
        vectors = self.embeddings.embed_documents(chunks)

        datapoints = [
            {
                "id": article_id,
                "feature_vector": vector,
            }
            for vector in vectors
        ]

        self.index.upsert(datapoints)

        return [
            {"chunk": chunk, "vector": vector}
            for chunk, vector in zip(chunks, vectors)
        ]
