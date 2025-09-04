import uuid 
from typing import List, Dict, Any
from services.vector_store_client import VectorStoreSingleton
from dotenv import load_dotenv
import os
from database.manager import DatabaseManager

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
            datapoint_id = str(article_id) + "/" + str(uuid.uuid4())
            generated_ids.append(datapoint_id)
            datapoints.append({
                "datapoint_id": datapoint_id,
                "feature_vector": vector,
            })

        deployed_index_id = os.getenv("DEPLOYED_INDEX_ID")
        if not deployed_index_id:
            raise ValueError("DEPLOYED_INDEX_ID must be implemented in .env")
        
        self.index.upsert_datapoints(datapoints=datapoints)
        
        return [
            {"chunk": chunk, "vector": vector, "vector_id": vector_id}
            for chunk, vector, vector_id in zip(chunks, vectors, generated_ids)
        ]
    def search_similar(self, query: str, k: int = 10) -> Dict[str, Any]:
        """
        Searches for 'K' articles similar to the given query.
        """
        query_embedding = self.embeddings.embed_query(query)

        deployed_index_id = os.getenv("DEPLOYED_INDEX_ID")
        response = self.endpoint.find_neighbors(
            deployed_index_id=deployed_index_id,
            queries=[query_embedding],
            num_neighbors=k
        )

        print(f"Search response: {response}")

        if not response or not response[0]:
            return {"query": query, "results": []}

        neighbors = response[0]

        article_ids = set()
        for neighbor in neighbors:
            raw_id = neighbor.id  # ej: "32/843b26d7-0dd2-4157-96fa-22f076524a85"
            if raw_id and "/" in raw_id:
                article_id = raw_id.split("/")[0]  
                if article_id.isdigit():
                    article_ids.add(int(article_id))

        print(f"Quantity of unique articles found: {len(article_ids)}")
        print(f"Article IDs: {article_ids}")

        db = DatabaseManager()
        articles = {a.id: a for a in (db.get_article_by_id(aid) for aid in article_ids) if a is not None}
        
        

        return {"query": query, "results": articles}
