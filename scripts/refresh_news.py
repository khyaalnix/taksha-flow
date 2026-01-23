#!/usr/bin/env python3
"""
News refresh script for Airflow DAG or cron job.

Usage:
    python scripts/refresh_news.py [--no-summarize] [--page-size N]

This script:
1. Fetches news from NewsAPI for all categories
2. Summarizes articles using AI (unless --no-summarize)
3. Caches results in Redis with TTL

Schedule: Run every 15-20 minutes via Airflow or cron:
    */15 * * * * cd /path/to/taksha-flow && python scripts/refresh_news.py
"""
import sys
import asyncio
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.news_service import news_service
from app.utils.logger import LoggerFactory

logger = LoggerFactory().get_logger()


async def refresh_news(page_size: int = 10, summarize: bool = True):
    """
    Main function to refresh all news categories.
    """
    logger.info(f"Starting news refresh (page_size={page_size}, summarize={summarize})")

    try:
        results = await news_service.fetch_and_cache_all_categories(
            page_size=page_size,
            summarize=summarize
        )

        # Log summary
        for category, batch in results.items():
            article_count = len(batch.articles)
            logger.info(f"  {category.value}: {article_count} articles")

        total = sum(len(b.articles) for b in results.values())
        logger.info(f"News refresh completed: {total} total articles cached")

        return True

    except Exception as e:
        logger.error(f"News refresh failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Refresh news cache")
    parser.add_argument(
        "--no-summarize",
        action="store_true",
        help="Skip AI summarization (faster, uses descriptions)"
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=10,
        help="Number of articles per category (default: 10)"
    )

    args = parser.parse_args()

    success = asyncio.run(refresh_news(
        page_size=args.page_size,
        summarize=not args.no_summarize
    ))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
