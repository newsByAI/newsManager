import os
from dotenv import load_dotenv
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_vertexai import VertexAIEmbeddings

load_dotenv()


class AIClientsSingleton:
    """
    Singleton class that manage the AI clients (embeddings and chunker)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:

            project_id = os.getenv("GCP_PROJECT_ID")
            location = os.getenv("GCP_LOCATION")

            if not project_id or not location:
                raise ValueError(
                    "GCP_PROJECT_ID and GCP_LOCATION must be set in your .env file"
                )

            cls._instance = super(AIClientsSingleton, cls).__new__(cls)

            cls._instance.embeddings_client = VertexAIEmbeddings(
                project=project_id, location=location, model_name="text-embedding-004"
            )

            cls._instance.semantic_chunker = SemanticChunker(
                cls._instance.embeddings_client,
                breakpoint_threshold_type="percentile",  # There is "perceWntile" (It should have a big sematic valley to do the chunking. 0.95 by default), "gradient", "standard_deviation"
                breakpoint_threshold_amount=45,
            )

        return cls._instance
