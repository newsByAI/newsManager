# Implements simple Factory Pattern for News Providers creation based on a string key.

from typing import Type, Dict
from .providers import NewsProvider, NewsApiAdapter

class NewsProviderFactory:
    _providers: Dict[str, Type[NewsProvider]] = {
        "newsapi": NewsApiAdapter,
    }

    @classmethod
    def get_provider(cls, source: str) -> NewsProvider:
        if source not in cls._providers:
            raise ValueError(f"News source '{source}' is not supported.")
        return cls._providers[source]()
