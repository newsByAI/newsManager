import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from ingestion.models import Article
from uses_cases.article_ingestion import ArticleIngestionService, ArticleIngestionError
from uses_cases.search_service import SearchService, SearchError


load_dotenv()


app = FastAPI(
    title="News Ingestion Service",
    description="An API to fetch articles from different sources.",
)

# Orígenes permitidos (dev y prod)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

domain_urls = os.getenv("DOMAIN_URL", "")
if domain_urls:
    origins += [url.strip() for url in domain_urls.split(",") if url.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # o usa ["*"] si no manejas credenciales
    allow_credentials=True,  # pon True solo si usas cookies/autenticación de navegador
    allow_methods=["*"],  # GET, POST, etc.
    allow_headers=["*"],  # Authorization, Content-Type, etc.
)

article_service = ArticleIngestionService()
search_service = SearchService()


@app.get("/api/v1/articles/{source}", response_model=str)
def get_articles_from_source(source: str, q: str):
    """
    Fetch, clean, store and index articles from a source.
    """
    try:
        return article_service.ingest_articles(source, q)

    except ArticleIngestionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")


@app.get("/api/v1/search")
def search_articles(q: str):
    """
    Endpoint to perform semantic search over stored articles.
    """
    try:
        return search_service.search_articles(q, k=10)
    except SearchError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error in semantic search: {e}"
        )
