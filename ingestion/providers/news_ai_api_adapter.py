import os
from typing import List
from ingestion.models import Article
from ingestion.providers.provider_i import NewsProvider
from eventregistry import EventRegistry, QueryArticlesIter
from dotenv import load_dotenv


class NewsAiApiAdapter(NewsProvider):
    """
    Adapter for the newsapi.ai (Event Registry) API that makes a real API call.
    """

    def __init__(self):
        """
        Initializes the adapter by loading the API key from environment variables
        and setting up the Event Registry client.
        """
        load_dotenv()
        self.api_key = os.getenv("NEWSAI_API_KEY")
        if not self.api_key:
            raise ValueError("NEWSAI_API_KEY environment variable not set.")

        # Initialize the Event Registry client once to be reused.
        # 'allowUseOfArchive=False' focuses on recent articles.
        self.er_client = EventRegistry(apiKey=self.api_key, allowUseOfArchive=False)

    def fetch_articles(self, query: str) -> List[Article]:
        """
        Fetches articles from the newsapi.ai API based on a search query.

        Args:
            query: The search term for finding articles.

        Returns:
            A list of Article objects matching the query.
        """
        print(f"Searching for '{query}' using NewsAPI.ai...")

        # Construct the query to search for English news articles
        q = QueryArticlesIter(keywords=query, lang="eng", dataType=["news", "pr"])

        articles = []
        try:
            # Execute the query, fetching a maximum of 5 recent articles
            # The SDK returns a generator, so we iterate through it
            response_articles = q.execQuery(
                self.er_client,
                sortBy="date",
                sortByAsc=False,
                maxItems=10,
            )

            for raw_article in response_articles:
                # Ensure the article has a title and URL before processing
                if not raw_article.get("title") or not raw_article.get("url"):
                    continue
                # Map the fields from the API response to our internal Article model
                print(raw_article.content)
                articles.append(
                    Article(
                        title=raw_article.get("title"),
                        content=raw_article.get("body"),
                        url=raw_article.get("url"),
                        published_at=raw_article.get("dateTime"),
                        content_preview=raw_article.get("body"),
                    )
                )
        except Exception as e:
            print(f"Error calling NewsAPI.ai: {e}")
            return []  # Return an empty list if an error occurs
        return articles
