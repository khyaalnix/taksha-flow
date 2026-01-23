from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class NewsCategory(str, Enum):
    """Master news categories matching NewsAPI categories."""
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    GENERAL = "general"
    HEALTH = "health"
    SCIENCE = "science"
    SPORTS = "sports"
    TECHNOLOGY = "technology"


class NewsArticle(BaseModel):
    """Raw news article from NewsAPI."""
    id: str
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    source_name: str
    author: Optional[str] = None
    published_at: datetime
    category: NewsCategory


class NewsSummary(BaseModel):
    """AI-summarized news item for dashboard display."""
    id: str
    title: str  # Original or shortened title
    summary: str  # AI-generated one-liner summary
    category: NewsCategory
    source_name: str
    image_url: Optional[str] = None
    url: str
    published_at: datetime
    # For bulletin-style reading
    bulletin_text: Optional[str] = None  # "In tech news, Apple announces..."


class CategoryNewsBatch(BaseModel):
    """Batch of news for a specific category."""
    category: NewsCategory
    articles: List[NewsSummary]
    fetched_at: datetime
    expires_at: datetime


class UserNewsRequest(BaseModel):
    """Request for user-specific news based on interests."""
    user_id: str
    interest_ids: List[str]
    max_per_category: int = Field(default=5, ge=1, le=20)


class NewsBulletin(BaseModel):
    """Aggregated news bulletin for a user."""
    items: List[NewsSummary]
    generated_at: datetime
    categories_included: List[NewsCategory]
