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

        # storage the best distance per article
        article_distances = {}  
        for neighbor in neighbors:
            raw_id = neighbor.id  #Based on the defined id structure: ex."32/843b26d7-0dd2-4157-96fa-22f076524a85"
            if raw_id and "/" in raw_id:
                article_id = raw_id.split("/")[0]
                if article_id.isdigit():
                    aid = int(article_id)
                    if aid not in article_distances or neighbor.distance < article_distances[aid]:
                        article_distances[aid] = neighbor.distance

        print(f"Quantity of unique articles found: {len(article_distances)}")
        print(f"Article IDs: {list(article_distances.keys())}")

        # --- Fetch articles from the database ---
        db = DatabaseManager()
        articles = {
            a.id: a for a in (db.get_article_by_id(aid) for aid in article_distances.keys())
            if a is not None
        }

        
        results = []
        for aid, article in articles.items():
            results.append({
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "published_at": article.published_at,
                "content_preview": article.content_preview,
                "distance": article_distances.get(aid)  
            })

        results.sort(key=lambda x: x["distance"])

        return {
            "query": query,
            "results": results[:k]  
        }
