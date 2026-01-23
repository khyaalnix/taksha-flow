"""
News service for fetching, summarizing, and caching news articles.

Pipeline:
1. Fetch news from NewsAPI by category
2. Summarize using AI
3. Cache in Redis with TTL
4. Serve to users based on their interests
"""
import json
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from app.client.news_client import news_client, NewsAPIClient
from app.services.ai.summarizer import ai_summarizer
from app.schemas.news import (
    NewsArticle,
    NewsSummary,
    NewsCategory,
    CategoryNewsBatch,
)
from app.utils.redis import RedisCache
from app.utils.logger import LoggerFactory

logger = LoggerFactory().get_logger()

# Redis key patterns
NEWS_CACHE_KEY = "flow:news:category:{category}"
NEWS_CACHE_TTL = 20 * 60  # 20 minutes


class NewsService:
    """Service for managing news content."""

    def __init__(self):
        self.news_client = news_client
        self.summarizer = ai_summarizer
        self.cache = RedisCache()

    def _cache_key(self, category: NewsCategory) -> str:
        """Generate cache key for a category."""
        return NEWS_CACHE_KEY.format(category=category.value)

    async def fetch_and_cache_category(
        self,
        category: NewsCategory,
        page_size: int = 10,
        summarize: bool = True
    ) -> CategoryNewsBatch:
        """
        Fetch news for a category, summarize, and cache.

        Args:
            category: News category to fetch
            page_size: Number of articles
            summarize: Whether to run AI summarization

        Returns:
            CategoryNewsBatch with summarized articles
        """
        # Fetch raw articles
        articles = await self.news_client.fetch_top_headlines(
            category=category,
            page_size=page_size
        )

        if not articles:
            logger.warning(f"No articles fetched for category: {category.value}")
            return CategoryNewsBatch(
                category=category,
                articles=[],
                fetched_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=NEWS_CACHE_TTL)
            )

        # Summarize articles
        summaries = []
        for article in articles:
            if summarize:
                summary_data = await self.summarizer.summarize_article(
                    title=article.title,
                    description=article.description,
                    content=article.content,
                    category=category.value
                )
                summary_text = summary_data["summary"]
                bulletin_text = summary_data["bulletin_text"]
            else:
                summary_text = article.description or article.title[:80]
                bulletin_text = f"In {category.value} news, {article.title}"

            summaries.append(NewsSummary(
                id=article.id,
                title=article.title,
                summary=summary_text,
                category=category,
                source_name=article.source_name,
                image_url=article.image_url,
                url=article.url,
                published_at=article.published_at,
                bulletin_text=bulletin_text
            ))

        now = datetime.now(timezone.utc)
        batch = CategoryNewsBatch(
            category=category,
            articles=summaries,
            fetched_at=now,
            expires_at=now + timedelta(seconds=NEWS_CACHE_TTL)
        )

        # Cache the batch
        cache_data = batch.model_dump(mode="json")
        await self.cache.set(
            self._cache_key(category),
            cache_data,
            NEWS_CACHE_TTL
        )

        logger.info(f"Cached {len(summaries)} articles for category: {category.value}")
        return batch

    async def fetch_and_cache_all_categories(
        self,
        page_size: int = 10,
        summarize: bool = True
    ) -> dict[NewsCategory, CategoryNewsBatch]:
        """
        Fetch and cache news for all categories.
        This is the main entry point for the Airflow DAG / cron job.
        """
        results = {}

        for category in NewsCategory:
            try:
                batch = await self.fetch_and_cache_category(
                    category=category,
                    page_size=page_size,
                    summarize=summarize
                )
                results[category] = batch
            except Exception as e:
                logger.error(f"Error fetching category {category.value}: {e}")
                results[category] = CategoryNewsBatch(
                    category=category,
                    articles=[],
                    fetched_at=datetime.now(timezone.utc),
                    expires_at=datetime.now(timezone.utc) + timedelta(seconds=NEWS_CACHE_TTL)
                )

        total_articles = sum(len(b.articles) for b in results.values())
        logger.info(f"Completed news refresh: {total_articles} articles across {len(results)} categories")

        return results

    async def get_cached_category(
        self,
        category: NewsCategory
    ) -> Optional[CategoryNewsBatch]:
        """
        Get cached news for a category.

        Returns:
            CategoryNewsBatch or None if not cached/expired
        """
        cache_key = self._cache_key(category)
        cached_data = await self.cache.get(cache_key)

        if not cached_data:
            return None

        try:
            return CategoryNewsBatch(**cached_data)
        except Exception as e:
            logger.error(f"Error parsing cached news for {category.value}: {e}")
            return None

    async def get_news_for_interests(
        self,
        interest_slugs: List[str],
        max_per_category: int = 3
    ) -> List[NewsSummary]:
        """
        Get news items for user based on their interest slugs.

        Maps interest slugs to news categories and returns relevant articles.

        Args:
            interest_slugs: List of user interest slugs (e.g., ["technology", "sports"])
            max_per_category: Max articles per category

        Returns:
            List of NewsSummary items
        """
        # Map interest slugs to news categories
        slug_to_category = {
            "technology": NewsCategory.TECHNOLOGY,
            "tech": NewsCategory.TECHNOLOGY,
            "business": NewsCategory.BUSINESS,
            "finance": NewsCategory.BUSINESS,
            "investing": NewsCategory.BUSINESS,
            "sports": NewsCategory.SPORTS,
            "fitness": NewsCategory.SPORTS,
            "entertainment": NewsCategory.ENTERTAINMENT,
            "movies": NewsCategory.ENTERTAINMENT,
            "music": NewsCategory.ENTERTAINMENT,
            "gaming": NewsCategory.ENTERTAINMENT,
            "health": NewsCategory.HEALTH,
            "wellness": NewsCategory.HEALTH,
            "science": NewsCategory.SCIENCE,
            "space": NewsCategory.SCIENCE,
        }

        # Get unique categories for user's interests
        categories = set()
        for slug in interest_slugs:
            slug_lower = slug.lower()
            if slug_lower in slug_to_category:
                categories.add(slug_to_category[slug_lower])

        # Default to general if no matches
        if not categories:
            categories = {NewsCategory.GENERAL, NewsCategory.TECHNOLOGY}

        # Fetch articles from each category
        all_articles = []
        for category in categories:
            batch = await self.get_cached_category(category)
            if batch and batch.articles:
                all_articles.extend(batch.articles[:max_per_category])

        # Sort by published date (newest first)
        all_articles.sort(key=lambda x: x.published_at, reverse=True)

        return all_articles

    async def get_priority_news_item(
        self,
        interest_slugs: List[str]
    ) -> Optional[dict]:
        """
        Get a single priority news item for the dashboard.
        Returns format suitable for PriorityItem.
        """
        articles = await self.get_news_for_interests(
            interest_slugs=interest_slugs,
            max_per_category=1
        )

        if not articles:
            return None

        top_article = articles[0]
        return {
            "id": f"news_{top_article.id}",
            "type": "news",
            "title": top_article.source_name,
            "subtitle": top_article.summary[:50] + "..." if len(top_article.summary) > 50 else top_article.summary
        }

    async def get_content_cards(
        self,
        interest_slugs: List[str],
        max_items: int = 3
    ) -> List[dict]:
        """
        Get news as content cards for the dashboard right sidebar.
        """
        articles = await self.get_news_for_interests(
            interest_slugs=interest_slugs,
            max_per_category=2
        )

        cards = []
        for article in articles[:max_items]:
            cards.append({
                "id": article.id,
                "title": article.source_name,
                "description": article.summary,
                "image_url": article.image_url,
                "source_url": article.url,
                "source_name": article.source_name,
                "bookmarked": False,
                "category": article.category.value
            })

        return cards


# Singleton instance
news_service = NewsService()
