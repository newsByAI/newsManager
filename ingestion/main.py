
from fastapi import FastAPI, HTTPException
from typing import List
from .factory import NewsProviderFactory
from .models import Article

app = FastAPI(
    title="News Ingestion Service",
    description="An API to fetch articles from different sources."
)

# We create a single factory instance for the entire application.
news_factory = NewsProviderFactory()

@app.get("/api/v1/articles/{source}", response_model=List[Article])
def get_articles_from_source(source: str, q: str):
    """
    Fetches articles from a specific source based on a query.
    - **source**: Identifier for the source (e.g., 'newsapi', 'theguardian').
    - **q**: The search term.
    """
    try:
        # 1. We ask the factory for the correct "translator" (adapter).
        provider = news_factory.get_provider(source)
        
        # 2. We use the adapter to get the articles (already in the standard format).
        articles = provider.fetch_articles(query=q)
        
        return articles
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")