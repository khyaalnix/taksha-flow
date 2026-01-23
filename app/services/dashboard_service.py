from datetime import datetime, timezone
from typing import List, Optional
import asyncio

from app.services.google.google_service import google_service
from app.services.news_service import news_service
from app.schemas.dashboard import (
    DashboardBrief,
    PriorityItem,
    PriorityItemType,
    DeepcastItem,
    ContentItem
)
from app.utils.logger import LoggerFactory

logger = LoggerFactory().get_logger()


class DashboardService:
    """Service for aggregating dashboard data from various sources."""

    def __init__(self):
        self.google_service = google_service
        self.news_service = news_service

    def _get_greeting(self) -> str:
        """Get time-appropriate greeting."""
        hour = datetime.now().hour
        if hour < 12:
            return "Good Morning"
        elif hour < 17:
            return "Good Afternoon"
        else:
            return "Good Evening"

    def _get_formatted_date(self) -> str:
        """Get formatted date string."""
        now = datetime.now()
        return now.strftime("%b %d, %Y")

    async def get_calendar_priority_items(
        self,
        user_id: str,
        max_items: int = 3
    ) -> List[PriorityItem]:
        """Get calendar events as priority items."""
        try:
            events = await self.google_service.get_upcoming_events(
                user_id,
                hours_ahead=24,
                max_results=max_items
            )

            priority_items = []
            for event in events:
                priority_items.append(PriorityItem(
                    id=event['id'],
                    type=PriorityItemType.EVENT,
                    title=event['title'],
                    subtitle=event['subtitle']
                ))

            return priority_items

        except Exception as e:
            logger.error(f"Error getting calendar priority items: {e}")
            return []

    async def get_email_priority_item(self, user_id: str) -> Optional[PriorityItem]:
        """Get email summary as a priority item."""
        try:
            email_item = await self.google_service.get_email_priority_item(user_id)

            if email_item:
                return PriorityItem(
                    id=email_item['id'],
                    type=PriorityItemType.EMAIL,
                    title=email_item['title'],
                    subtitle=email_item['subtitle']
                )
            return None

        except Exception as e:
            logger.error(f"Error getting email priority item: {e}")
            return None

    async def get_news_priority_item(self, interest_slugs: List[str] = None) -> Optional[PriorityItem]:
        """Get a news item based on user interests from cached news."""
        try:
            if not interest_slugs:
                interest_slugs = ["technology", "general"]

            news_item = await self.news_service.get_priority_news_item(interest_slugs)

            if news_item:
                return PriorityItem(
                    id=news_item['id'],
                    type=PriorityItemType.NEWS,
                    title=news_item['title'],
                    subtitle=news_item['subtitle']
                )
            return None

        except Exception as e:
            logger.error(f"Error getting news priority item: {e}")
            return None

    def get_mock_deepcast(self) -> DeepcastItem:
        """Get mock deepcast content (to be replaced with real content service)."""
        # TODO: Integrate with content/podcast service
        return DeepcastItem(
            id="deepcast_1",
            title="Are chickens really dinosaurs?",
            excerpt='"Exactly. If you compare a T-rex leg bone to a chicken\'s..."',
            image_url="https://images.unsplash.com/photo-1606567595334-d39972c85dfd?w=400&h=500&fit=crop",
            duration="0:42",
            progress=33,
            source="Deepcast"
        )

    async def get_content_items(self, interest_slugs: List[str] = None, max_items: int = 3) -> List[ContentItem]:
        """Get content items from cached news based on user interests."""
        try:
            if not interest_slugs:
                interest_slugs = ["technology", "general"]

            content_cards = await self.news_service.get_content_cards(
                interest_slugs=interest_slugs,
                max_items=max_items
            )

            items = []
            for card in content_cards:
                items.append(ContentItem(
                    id=card['id'],
                    title=card['title'],
                    description=card['description'],
                    image_url=card.get('image_url'),
                    source_url=card.get('source_url'),
                    source_name=card.get('source_name'),
                    bookmarked=card.get('bookmarked', False),
                    category=card.get('category')
                ))

            # Fallback to mock data if no cached news
            if not items:
                items = [
                    ContentItem(
                        id="content_1",
                        title="Foundry Industrials",
                        description='Unveils "Air" a new ultralight phone concept.',
                        image_url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=100&h=100&fit=crop",
                        source_name="Tech News"
                    ),
                    ContentItem(
                        id="content_2",
                        title="Weekend Plans",
                        description="The 12 best sushi spots in the Bay Area right now.",
                        image_url="https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=100&h=100&fit=crop",
                        source_name="Local Guide"
                    )
                ]

            return items

        except Exception as e:
            logger.error(f"Error getting content items: {e}")
            # Return mock data on error
            return [
                ContentItem(
                    id="content_1",
                    title="Foundry Industrials",
                    description='Unveils "Air" a new ultralight phone concept.',
                    image_url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=100&h=100&fit=crop",
                    source_name="Tech News"
                )
            ]

    def get_suggestion(self, priority_items: List[PriorityItem]) -> str:
        """Generate a contextual suggestion based on priority items."""
        # Find email items to generate a relevant suggestion
        for item in priority_items:
            if item.type == PriorityItemType.EMAIL:
                return f'"Hey Flow, summarize my unread emails."'

        # Find calendar items
        for item in priority_items:
            if item.type == PriorityItemType.EVENT:
                return f'"Hey Flow, what should I prepare for {item.title}?"'

        return '"Hey Flow, what\'s on my agenda today?"'

    async def get_dashboard_brief(
        self,
        user_id: str,
        user_name: str = "there",
        include_calendar: bool = True,
        include_email: bool = True,
        include_news: bool = True,
        max_priority_items: int = 5,
        interest_slugs: List[str] = None
    ) -> DashboardBrief:
        """Get the complete dashboard brief for a user."""

        priority_items: List[PriorityItem] = []
        urgent_count = 0

        # Default interests if not provided
        if not interest_slugs:
            interest_slugs = ["technology", "business", "general"]

        # Build async tasks for concurrent fetching
        async def get_calendar():
            if include_calendar:
                return await self.get_calendar_priority_items(user_id, max_items=3)
            return []

        async def get_email():
            if include_email:
                return await self.get_email_priority_item(user_id)
            return None

        async def get_news():
            if include_news:
                return await self.get_news_priority_item(interest_slugs)
            return None

        async def get_content():
            return await self.get_content_items(interest_slugs, max_items=3)

        try:
            # Fetch all data concurrently
            results = await asyncio.gather(
                get_calendar(),
                get_email(),
                get_news(),
                get_content(),
                return_exceptions=True
            )

            # Process calendar events
            if not isinstance(results[0], Exception):
                calendar_items = results[0] or []
                priority_items.extend(calendar_items)
                urgent_count += len(calendar_items)

            # Process email
            if not isinstance(results[1], Exception):
                email_item = results[1]
                if email_item:
                    priority_items.append(email_item)

            # Process news
            if not isinstance(results[2], Exception):
                news_item = results[2]
                if news_item:
                    priority_items.append(news_item)

            # Process content items
            if not isinstance(results[3], Exception):
                content_items = results[3] or []
            else:
                content_items = []

        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            content_items = []

        # Limit priority items
        priority_items = priority_items[:max_priority_items]

        # Get suggestion
        suggestion = self.get_suggestion(priority_items)

        # Get deepcast (still mock for now)
        deepcast = self.get_mock_deepcast()

        greeting = f"{self._get_greeting()}, {user_name}"

        return DashboardBrief(
            greeting=greeting,
            date=self._get_formatted_date(),
            priority_items=priority_items,
            urgent_count=urgent_count,
            suggestion=suggestion,
            deepcast=deepcast,
            content_items=content_items
        )


# Singleton instance
dashboard_service = DashboardService()
