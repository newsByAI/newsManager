# Defines the unified data model for articles to standardize data from various APIs.

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Article(BaseModel):
    """Our standardized article model."""
    title: str
    url: Optional[str] = Field(None, description="The URL of the article.")
    content: str
    source_name: Optional[str] = Field(None, description="The name of the source/publisher.") 
    published_at: Optional[datetime] = Field(None, description="The publication date of the article.")
    content_preview: Optional[str] = Field(None, description="A brief summary or description of the article.")