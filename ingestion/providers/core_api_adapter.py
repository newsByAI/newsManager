import os
import requests
from typing import List
from datetime import date
from ingestion.models import Article
from dotenv import load_dotenv
from ingestion.providers.provider_i import NewsProvider


class CoreApiAdapter(NewsProvider):
    """Adapter for the CORE API that makes a real API call."""

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("CORE_API_KEY")
        if not self.api_key:
            raise ValueError("CORE_API_KEY environment variable not set.")
        self.base_url = "https://api.core.ac.uk/v3/search/works"

    def fetch_articles(self, query: str) -> List[Article]:
        print(f"Searching for '{query}' using CORE API...")

        search_query = f'(title:"{query}") AND _exists_:fullText'

        headers = {"Authorization": f"Bearer {self.api_key}"}

        params = {"q": search_query, "limit": 1}

        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling CORE API: {e}")
            return []

        articles = []
        for raw_article in data.get("results", []):
            if not raw_article.get("title") or not raw_article.get("downloadUrl"):
                continue

            raw_content = raw_article.get("fullText", "")
            print(raw_content)
            articles.append(
                Article(
                    title=raw_article.get("title"),
                    url=raw_article.get("url"),
                    content=raw_content,
                    published_at=raw_article.get("publishedDate"),
                    content_preview=raw_article.get("abstract"),
                )
            )
        return articles
