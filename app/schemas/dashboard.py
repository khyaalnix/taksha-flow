from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class PriorityItemType(str, Enum):
    EVENT = "event"
    EMAIL = "email"
    NEWS = "news"
    TASK = "task"


class PriorityItem(BaseModel):
    """A priority item for the dashboard (calendar event, email, news, etc.)"""
    id: str
    type: PriorityItemType
    title: str
    subtitle: str
    timestamp: Optional[datetime] = None
    metadata: Optional[dict] = None


class DeepcastItem(BaseModel):
    """A deepcast/podcast item for audio content"""
    id: str
    title: str
    excerpt: str
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    duration: str = "0:00"
    progress: int = Field(default=0, ge=0, le=100)
    source: Optional[str] = None


class ContentItem(BaseModel):
    """A content card item (news, articles, etc.)"""
    id: str
    title: str
    description: str
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    bookmarked: bool = False
    category: Optional[str] = None


class DashboardBrief(BaseModel):
    """The complete dashboard brief response"""
    greeting: str
    date: str
    priority_items: List[PriorityItem] = []
    urgent_count: int = 0
    suggestion: Optional[str] = None
    deepcast: Optional[DeepcastItem] = None
    content_items: List[ContentItem] = []


class CalendarEvent(BaseModel):
    """A calendar event from Google Calendar"""
    id: str
    summary: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    attendees: List[str] = []
    is_all_day: bool = False


class EmailSummary(BaseModel):
    """Summary of unread emails"""
    total_unread: int = 0
    top_sender: Optional[str] = None
    top_subject: Optional[str] = None
    priority_emails: List[dict] = []


class DashboardRequest(BaseModel):
    """Optional request parameters for dashboard"""
    include_calendar: bool = True
    include_email: bool = True
    include_news: bool = True
    max_priority_items: int = Field(default=5, ge=1, le=10)
    max_content_items: int = Field(default=5, ge=1, le=10)
