# ingestion/providers.py - Implements the Adapter Pattern for NewsAPI.

import os
import requests
from abc import ABC, abstractmethod
from typing import List
from datetime import date
from .models import Article
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Interface (The Adapter Contract) ---
class NewsProvider(ABC):
    """Interface that all news providers must implement."""
    @abstractmethod
    def fetch_articles(self, query: str) -> List[Article]:
        pass

# --- Concrete Adapter for NewsAPI ---

class NewsApiAdapter(NewsProvider):
    """Adapter for the newsapi.org API that makes a real API call."""

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        if not self.api_key:
            raise ValueError("NEWS_API_KEY environment variable not set.")
        self.base_url = "https://newsapi.org/v2/everything"

    def fetch_articles(self, query: str) -> List[Article]:
        print(f"Searching for '{query}' using NewsAPI...")

        params = {
            "q": query,
            "from": date.today().isoformat(), 
            "sortBy": "popularity",
            "apiKey": self.api_key,
            "language": "en" 
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling NewsAPI: {e}")
            return []

        
        articles = []
        for raw_article in data.get("articles", []):
        
            if not raw_article.get("title") or not raw_article.get("url"):
                continue
            
            articles.append(
                Article(
                    title=raw_article.get("title"),
                    content=raw_article.get("content"),
                    url=raw_article.get("url"),
                    source_name=raw_article.get("source", {}).get("name"),
                    published_at=raw_article.get("publishedAt"),
                    content_preview=raw_article.get("description")
                )
            )
        return articles