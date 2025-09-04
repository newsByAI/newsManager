# services/article_service.py
import logging
from ingestion.factory import NewsProviderFactory
from ingestion.models import Article
from cleaning.cleaner import Cleaner
from database.manager import DatabaseManager
from chunking.chunker import DocumentChunker
from chunking.strategies.semantic import SemanticChunkingStrategy
from storage.vector_store import VectorStore

logger = logging.getLogger(__name__)

class ArticleIngestionError(Exception):
    """Base exception for ingestion errors."""

class ArticleIngestionService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.news_factory = NewsProviderFactory()
        self.cleaner = Cleaner()
        self.chunker = DocumentChunker(strategy=SemanticChunkingStrategy())
        self.vector_store = VectorStore()

    def ingest_articles(self, source: str, query: str) -> str:
        try:
            # 1. Fetch articles from external source
            provider = self.news_factory.get_provider(source)
            articles = provider.fetch_articles(query=query)

            if not articles:
                msg = "No articles found from the external source."
                logger.warning(msg)
                return msg

            # 2. Avoid duplicates
            new_articles = [
                article for article in articles
                if not self.db_manager.article_exists_by_title(article.title)
            ]
            if not new_articles:
                msg = "No new articles to process. All fetched articles already exist."
                logger.info(msg)
                return msg

            # 3. Clean articles
            clean_articles = []
            for a in new_articles:
                try:
                    clean_content = self.cleaner.clean(a.content)
                    clean_articles.append(
                        Article(
                            title=a.title,
                            url=a.url,
                            content=clean_content,
                            published_at=a.published_at,
                            content_preview=a.content_preview,
                        )
                    )
                except Exception as e:
                    logger.error(f"Failed to clean article '{a.title}': {e}", exc_info=True)

            if not clean_articles:
                msg = "All new articles failed during cleaning."
                logger.error(msg)
                return msg

            # 4. Store metadata in DB
            article_ids = []
            id_to_article = {}
            for a in clean_articles:
                try:
                    aid = self.db_manager.add_article(a)
                    article_ids.append(aid)
                    id_to_article[aid] = a
                except Exception as e:
                    logger.error(f"Failed to store article '{a.title}' in DB: {e}", exc_info=True)

            if not article_ids:
                msg = "Failed to store any articles in the database."
                logger.error(msg)
                return msg

            # 5. Chunking + Vectorization + Storage
            for aid, article in id_to_article.items():
                try:
                    chunks = self.chunker.chunk(article)
                    if not chunks:
                        logger.warning(f"No chunks generated for article '{article.title}' (ID {aid})")
                        continue
                    self.vector_store.vectorize_and_store(aid, chunks)
                except Exception as e:
                    logger.error(
                        f"Failed to process chunks for article '{article.title}' (ID {aid}): {e}",
                        exc_info=True
                    )

            return f"Successfully processed and stored {len(article_ids)} articles."

        except Exception as e:
            logger.critical(f"Unexpected ingestion error: {e}", exc_info=True)
            raise ArticleIngestionError("Ingestion process failed") from e
