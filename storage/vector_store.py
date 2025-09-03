import uuid 
from typing import List, Dict
from services.vector_store_client import VectorStoreSingleton
from dotenv import load_dotenv
import os

load_dotenv()

class VectorStore:
    """
    Manage vectorization and storage in Vertex AI Search.
    """

    def __init__(self):
        self.client = VectorStoreSingleton()
        self.embeddings = self.client.embeddings
        self.endpoint = self.client.endpoint
        self.index = self.client.index

    def vectorize_and_store(self, article_id: int, chunks: List[str]) -> List[Dict]:
        """
        Generates embeddings for the given chunks and stores them in Vertex AI Search.
        """
        vectors = self.embeddings.embed_documents(chunks)
        datapoints = []
        
        generated_ids = []

        for vector in vectors:
            datapoint_id = str(uuid.uuid4())
            generated_ids.append(datapoint_id)
            datapoints.append({
                "datapoint_id": datapoint_id,
                "feature_vector": vector,
                "restricts": [
                    {
                        "namespace": "article_id",
                        "allow_list": [str(article_id)]
                    }
                ]
            })

        deployed_index_id = os.getenv("DEPLOYED_INDEX_ID")
        if not deployed_index_id:
            raise ValueError("DEPLOYED_INDEX_ID must be implemented in .env")
        
        self.index.upsert_datapoints(datapoints=datapoints)
        
        return [
            {"chunk": chunk, "vector": vector, "vector_id": vector_id}
            for chunk, vector, vector_id in zip(chunks, vectors, generated_ids)
        ]