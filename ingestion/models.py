# Defines the unified data model for articles to standardize data from various APIs.

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Article(BaseModel):
    """Our standardized article model."""
    title: str
    url: str
    content: str
    source_name: str
    published_at: datetime
    content_preview: Optional[str] = Field(None, description="A brief summary or description of the article.")