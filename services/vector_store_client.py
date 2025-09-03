import os
from services.ai_clients import AIClientsSingleton
from google.cloud import aiplatform

class VectorStoreSingleton:
    """
    Singleton class that manages the connection to Vertex AI Search.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStoreSingleton, cls).__new__(cls)


            clients = AIClientsSingleton()
            cls._instance.embeddings = clients.embeddings_client

            project_id = os.getenv("GCP_PROJECT_ID")
            location = os.getenv("GCP_LOCATION")
            index_id = os.getenv("VERTEX_INDEX_ID")       
            endpoint_id = os.getenv("VERTEX_ENDPOINT_ID") 

            if not project_id or not location:
                raise ValueError("GCP_PROJECT_ID y GCP_LOCATION deben estar configurados en el .env")

            cls._instance.project_id = project_id
            cls._instance.location = location
            cls._instance.index_id = index_id
            cls._instance.endpoint_id = endpoint_id


            aiplatform.init(project=project_id, location=location)

            cls._instance.index = aiplatform.MatchingEngineIndex(index_name=index_id)
            cls._instance.endpoint = aiplatform.MatchingEngineIndexEndpoint(
                index_endpoint_name=endpoint_id
            )

        return cls._instance


