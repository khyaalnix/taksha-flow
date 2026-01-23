"""
News API endpoints.

Provides:
- Get news for user based on interests
- Trigger news refresh (for admin/Airflow)
- Get news by category
"""
import json
from fastapi import APIRouter, Depends, Query, HTTPException, status, Header
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
from typing import List, Optional

from app.core.security import get_current_user
from app.services.news_service import news_service
from app.schemas.news import NewsCategory, NewsSummary
from configs.settings import RATE_LIMITER_CONFIG

from app.utils.logger import LoggerFactory

logger = LoggerFactory().get_logger()

with open(RATE_LIMITER_CONFIG, "r") as f:
    rate_limiter_config = json.load(f)

router = APIRouter(
    prefix="/news",
    tags=["news"],
    dependencies=[Depends(RateLimiter(**rate)) for rate in rate_limiter_config["app"]]
)


@router.get("/feed", status_code=status.HTTP_200_OK)
async def get_news_feed(
    categories: Optional[str] = Query(
        default=None,
        description="Comma-separated category slugs (e.g., 'technology,sports')"
    ),
    max_per_category: int = Query(default=5, ge=1, le=20),
    current_user: dict = Depends(get_current_user),
):
    """
    Get personalized news feed based on user interests or specified categories.
    """
    try:
        # Parse categories or use user interests
        if categories:
            interest_slugs = [c.strip() for c in categories.split(",")]
        else:
            # TODO: Fetch user interests from database
            # For now, default to general categories
            interest_slugs = ["technology", "business", "general"]

        articles = await news_service.get_news_for_interests(
            interest_slugs=interest_slugs,
            max_per_category=max_per_category
        )

        return JSONResponse(content={
            "message": "News feed retrieved successfully",
            "data": [article.model_dump(mode="json") for article in articles],
            "total": len(articles)
        })

    except Exception as e:
        logger.error(f"Error getting news feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch news feed"
        )


@router.get("/category/{category}", status_code=status.HTTP_200_OK)
async def get_news_by_category(
    category: str,
    max_items: int = Query(default=10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    """
    Get news for a specific category.
    """
    try:
        # Validate category
        try:
            news_category = NewsCategory(category.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Valid options: {[c.value for c in NewsCategory]}"
            )

        batch = await news_service.get_cached_category(news_category)

        if not batch or not batch.articles:
            return JSONResponse(content={
                "message": "No cached news for this category",
                "data": [],
                "total": 0
            })

        articles = batch.articles[:max_items]

        return JSONResponse(content={
            "message": f"News for {category} retrieved successfully",
            "data": [article.model_dump(mode="json") for article in articles],
            "total": len(articles),
            "fetched_at": batch.fetched_at.isoformat(),
            "expires_at": batch.expires_at.isoformat()
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting news for category {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch news"
        )


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def trigger_news_refresh(
    page_size: int = Query(default=10, ge=1, le=50),
    summarize: bool = Query(default=True),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
):
    """
    Trigger a news refresh for all categories.

    This endpoint can be called by:
    - Airflow HTTP Operator
    - Admin users with API key
    - Cron jobs

    Note: This should be protected in production with an API key or internal network access.
    """
    # TODO: Add proper API key validation for production
    # For now, allow the refresh to proceed

    try:
        logger.info(f"News refresh triggered (page_size={page_size}, summarize={summarize})")

        results = await news_service.fetch_and_cache_all_categories(
            page_size=page_size,
            summarize=summarize
        )

        summary = {
            category.value: len(batch.articles)
            for category, batch in results.items()
        }

        total = sum(summary.values())

        return JSONResponse(content={
            "message": "News refresh completed",
            "total_articles": total,
            "by_category": summary
        })

    except Exception as e:
        logger.error(f"Error during news refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"News refresh failed: {str(e)}"
        )


@router.get("/categories", status_code=status.HTTP_200_OK)
async def get_available_categories():
    """
    Get list of available news categories.
    """
    return JSONResponse(content={
        "categories": [
            {"value": c.value, "label": c.value.title()}
            for c in NewsCategory
        ]
    })
