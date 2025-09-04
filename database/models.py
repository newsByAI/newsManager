from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ArticleModel(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    url = Column(Text)
    published_at = Column(TIMESTAMP)
    content_preview = Column(Text)

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:30]}...')>" 