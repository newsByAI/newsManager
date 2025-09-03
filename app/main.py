
from fastapi import FastAPI, HTTPException
from typing import List
from ingestion.factory import NewsProviderFactory
from ingestion.models import Article
from cleaning.cleaner import Cleaner
from database.manager import DatabaseManager
from chunking.chunker import DocumentChunker
from chunking.strategies.semantic import SemanticChunkingStrategy
from storage.vector_store import VectorStore

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
    - **source**: Identifier for the source (e.g., 'newsapi')
    - **q**: The search term.
    """
    try:
        # 1. We ask the factory for the correct "translator" (adapter).
        provider = news_factory.get_provider(source)
        
        # 2. We use the adapter to get the articles (already in the standard format).
        articles = provider.fetch_articles(query=q)
        
        
        # 3. Must clean each article content using the Cleaner class.
        
        cleaner = Cleaner()
        clean_articles = [ Article(
            title=article.title,
            url=article.url,
            content=cleaner.clean(article.content),
            published_at=article.published_at,
            content_preview=article.content_preview
        ) for article in articles ]
            
        # 4. Must store the metada of the articles in the database.
        
        articles_ids= [ DatabaseManager().add_article(article) for article in clean_articles ]
        id_to_article = {id: article for id, article in zip(articles_ids, clean_articles)}
        
        print(f"Stored {len(articles_ids)} articles in the database with IDs: {articles_ids}")
        # 5. Must create chunks and store them in the vector store and store the IDs to then use them.


        chunker = DocumentChunker(strategy=SemanticChunkingStrategy())
        
        print("Initializing vector store...")
        
        vector_store = VectorStore()
        
        for id, article in id_to_article.items():
            chunks = chunker.chunk(article.content)
            print(f"Article ID {id} chunked into {len(chunks)} chunks.")
            vector_store.vectorize_and_store(id, chunks)        
    
        return articles
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")