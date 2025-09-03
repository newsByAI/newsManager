import os
from typing import List
from datetime import date
from ingestion.models import Article
from ingestion.providers.provider_i import NewsProvider
from perigon import ApiClient, V1Api
from dotenv import load_dotenv


class PerigonAdapter(NewsProvider):
    """Adapter for the perigon API that makes a real API call."""

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("PERIGON_API_KEY")
        if not self.api_key:
            raise ValueError("PERIGON_API_KEY environment variable not set.")

    def fetch_articles(self, query: str) -> List[Article]:
        print(f"Searching for '{query}' using PerigonAPI...")

        client = ApiClient(api_key=self.api_key)
        api = V1Api(client)

        try:
            response = api.search_articles(
                q=query, language="en", var_from=date.today().isoformat(), size=5
            )
        except Exception as e:
            print(f"Error calling NewsAPI: {e}")
            return []

        print(response.articles[0].title)
        articles = []

        for raw_article in response.articles:
            print(raw_article)
            if not raw_article.title or not raw_article.url:
                continue

            articles.append(
                Article(
                    title=raw_article.title,
                    content=raw_article.content,
                    url=raw_article.url,
                    published_at=raw_article.pub_date,
                    content_preview=raw_article.description,
                )
            )
        return articles
