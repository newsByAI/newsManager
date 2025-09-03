# database/manager.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, ArticleModel
from ingestion.models import Article as ArticleSchema 
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating new DatabaseManager instance...")
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            
            db_user = os.getenv("POSTGRES_USER", "news_user")
            db_pass = os.getenv("POSTGRES_PASSWORD", "news_pass")
            db_name = os.getenv("POSTGRES_DB", "news_db")
            db_host = "localhost" 
            
            database_url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:5432/{db_name}"
            
            cls._instance.engine = create_engine(database_url)
            Base.metadata.create_all(cls._instance.engine) # Crea la tabla si no existe
            cls._instance.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls._instance.engine)
        return cls._instance

    def add_article(self, article_data: ArticleSchema) -> int:
        """
        Adds a new article to the database and returns its ID.
        """
        db = self.SessionLocal()
        try:
            new_article = ArticleModel(
                title=article_data.title,
                url=article_data.url,
                published_at=article_data.published_at,
                content_preview=article_data.content_preview
            )
            db.add(new_article)
            db.commit()
            db.refresh(new_article)
            print(f"Article added to PostgreSQL with ID: {new_article.id}")
            return new_article.id
        finally:
            db.close()

    def get_article_by_id(self, article_id: int) -> ArticleModel:
        """
        Retrieves an article by its primary key ID.
        """
        db = self.SessionLocal()
        try:
            return db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
        finally:
            db.close()      