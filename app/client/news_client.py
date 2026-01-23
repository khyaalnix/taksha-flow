"""
NewsAPI client for fetching news articles.
Documentation: https://newsapi.org/docs/endpoints
"""
import httpx
from typing import List, Optional
from datetime import datetime, timezone
import hashlib

from configs.settings import NEWSAPI_KEY, NEWSAPI_BASE_URL
from app.schemas.news import NewsArticle, NewsCategory
from app.utils.logger import LoggerFactory

logger = LoggerFactory().get_logger()


class NewsAPIClient:
    """Client for NewsAPI.org"""

    def __init__(self):
        self.api_key = NEWSAPI_KEY
        self.base_url = NEWSAPI_BASE_URL

    def _generate_article_id(self, url: str) -> str:
        """Generate a consistent ID from article URL."""
        return hashlib.md5(url.encode()).hexdigest()[:12]

    async def fetch_top_headlines(
        self,
        category: NewsCategory,
        country: str = "us",
        page_size: int = 10
    ) -> List[NewsArticle]:
        """
        Fetch top headlines for a specific category.

        Args:
            category: News category (business, tech, sports, etc.)
            country: Country code (default: us)
            page_size: Number of articles to fetch (max 100)

        Returns:
            List of NewsArticle objects
        """
        if not self.api_key:
            logger.warning("NEWSAPI_KEY not configured, returning empty results")
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/top-headlines",
                    params={
                        "apiKey": self.api_key,
                        "category": category.value,
                        "country": country,
                        "pageSize": page_size,
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                if data.get("status") != "ok":
                    logger.error(f"NewsAPI error: {data.get('message')}")
                    return []

                articles = []
                for article in data.get("articles", []):
                    # Skip articles with missing essential fields
                    if not article.get("title") or not article.get("url"):
                        continue

                    # Skip removed articles
                    if article.get("title") == "[Removed]":
                        continue

                    try:
                        published_at = datetime.fromisoformat(
                            article["publishedAt"].replace("Z", "+00:00")
                        )
                    except (ValueError, KeyError):
                        published_at = datetime.now(timezone.utc)

                    articles.append(NewsArticle(
                        id=self._generate_article_id(article["url"]),
                        title=article["title"],
                        description=article.get("description"),
                        content=article.get("content"),
                        url=article["url"],
                        image_url=article.get("urlToImage"),
                        source_name=article.get("source", {}).get("name", "Unknown"),
                        author=article.get("author"),
                        published_at=published_at,
                        category=category
                    ))

                logger.info(f"Fetched {len(articles)} articles for category: {category.value}")
                return articles

        except httpx.HTTPStatusError as e:
            logger.error(f"NewsAPI HTTP error for {category.value}: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error fetching news for {category.value}: {e}")
            return []

    async def fetch_all_categories(
        self,
        country: str = "us",
        page_size: int = 10
    ) -> dict[NewsCategory, List[NewsArticle]]:
        """
        Fetch top headlines for all categories.

        Returns:
            Dict mapping category to list of articles
        """
        results = {}

        for category in NewsCategory:
            articles = await self.fetch_top_headlines(
                category=category,
                country=country,
                page_size=page_size
            )
            results[category] = articles

        total = sum(len(articles) for articles in results.values())
        logger.info(f"Fetched {total} articles across {len(NewsCategory)} categories")

        return results

    async def search_news(
        self,
        query: str,
        page_size: int = 10,
        sort_by: str = "relevancy"
    ) -> List[NewsArticle]:
        """
        Search for news articles by keyword.
        Useful for custom interest-based searches.

        Args:
            query: Search query (keywords)
            page_size: Number of results
            sort_by: relevancy, popularity, or publishedAt
        """
        if not self.api_key:
            logger.warning("NEWSAPI_KEY not configured, returning empty results")
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/everything",
                    params={
                        "apiKey": self.api_key,
                        "q": query,
                        "pageSize": page_size,
                        "sortBy": sort_by,
                        "language": "en",
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                if data.get("status") != "ok":
                    logger.error(f"NewsAPI search error: {data.get('message')}")
                    return []

                articles = []
                for article in data.get("articles", []):
                    if not article.get("title") or not article.get("url"):
                        continue
                    if article.get("title") == "[Removed]":
                        continue

                    try:
                        published_at = datetime.fromisoformat(
                            article["publishedAt"].replace("Z", "+00:00")
                        )
                    except (ValueError, KeyError):
                        published_at = datetime.now(timezone.utc)

                    articles.append(NewsArticle(
                        id=self._generate_article_id(article["url"]),
                        title=article["title"],
                        description=article.get("description"),
                        content=article.get("content"),
                        url=article["url"],
                        image_url=article.get("urlToImage"),
                        source_name=article.get("source", {}).get("name", "Unknown"),
                        author=article.get("author"),
                        published_at=published_at,
                        category=NewsCategory.GENERAL  # Default for search results
                    ))

                return articles

        except Exception as e:
            logger.error(f"Error searching news for '{query}': {e}")
            return []


# Singleton instance
news_client = NewsAPIClient()
