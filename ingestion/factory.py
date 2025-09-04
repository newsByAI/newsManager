# Implements simple Factory Pattern for News Providers creation based on a string key.

from typing import Type, Dict
from ingestion.providers.provider_i import NewsProvider
from ingestion.providers.news_api_adapter import NewsApiAdapter
from ingestion.providers.core_api_adapter import CoreApiAdapter
from ingestion.providers.perigon_adapter import PerigonAdapter
from ingestion.providers.news_ai_api_adapter import NewsAiApiAdapter


class NewsProviderFactory:
    _providers: Dict[str, Type[NewsProvider]] = {
        "newsapi": NewsApiAdapter,
        "core": CoreApiAdapter,
        "news-ai": NewsAiApiAdapter,
        "perigon": PerigonAdapter,
    }

    @classmethod
    def get_provider(cls, source: str) -> NewsProvider:
        if source not in cls._providers:
            raise ValueError(f"News source '{source}' is not supported.")
        return cls._providers[source]()
