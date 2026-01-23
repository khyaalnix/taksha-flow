"""
Dashboard API endpoints for fetching aggregated user data.

Provides:
- Dashboard brief (priority items, deepcast, content cards)
- Calendar events summary
- Email summary
"""
import json
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter

from app import getAppState, AppState
from app.core.security import get_current_user
from app.services.dashboard_service import dashboard_service
from app.schemas.dashboard import DashboardBrief, DashboardRequest
from app.utils.utility import get_collection
from configs.settings import RATE_LIMITER_CONFIG, FLOW_DATABASE, Collection

from app.utils.logger import LoggerFactory
logger = LoggerFactory().get_logger()

with open(RATE_LIMITER_CONFIG, "r") as f:
    rate_limiter_config = json.load(f)


async def get_user_interest_slugs(app_state: AppState, user_email: str) -> List[str]:
    """Fetch user's interest IDs/slugs from the database."""
    try:
        collection = await get_collection(
            app_state.resources['mongo'],
            FLOW_DATABASE,
            Collection.INTERESTS
        )
        cursor = collection.find({"name": user_email})
        interests = await cursor.to_list(length=None)

        # Return interest_ids as slugs
        return [interest["interest_id"] for interest in interests]
    except Exception as e:
        logger.error(f"Error fetching user interests: {e}")
        return []

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(RateLimiter(**rate)) for rate in rate_limiter_config["app"]]
)


@router.get("/brief", status_code=status.HTTP_200_OK, response_model=DashboardBrief)
async def get_dashboard_brief(
    include_calendar: bool = Query(default=True, description="Include calendar events"),
    include_email: bool = Query(default=True, description="Include email summary"),
    include_news: bool = Query(default=True, description="Include news items"),
    max_priority_items: int = Query(default=5, ge=1, le=10, description="Maximum priority items"),
    current_user: dict = Depends(get_current_user),
    app_state: AppState = Depends(getAppState),
):
    """
    Get the complete dashboard brief for the authenticated user.

    This endpoint aggregates data from:
    - Google Calendar (upcoming events)
    - Gmail (unread email summary)
    - News feed (based on user interests)
    - Deepcast content
    - Content recommendations

    Returns a structured dashboard brief suitable for rendering the main dashboard.
    """
    try:
        user_name = current_user.get("name", "there")
        if user_name:
            # Get first name only
            user_name = user_name.split()[0]

        # Fetch user interests for personalized news
        interest_slugs = await get_user_interest_slugs(
            app_state,
            current_user.get("email", "")
        )

        brief = await dashboard_service.get_dashboard_brief(
            user_id=current_user["user_id"],
            user_name=user_name,
            include_calendar=include_calendar,
            include_email=include_email,
            include_news=include_news,
            max_priority_items=max_priority_items,
            interest_slugs=interest_slugs if interest_slugs else None
        )

        return brief

    except Exception as e:
        logger.error(f"Error getting dashboard brief: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard data"
        )


@router.get("/calendar/today", status_code=status.HTTP_200_OK)
async def get_todays_calendar_events(
    max_events: int = Query(default=10, ge=1, le=20, description="Maximum events to return"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get today's calendar events for the authenticated user.

    Returns a list of calendar events scheduled for today.
    """
    try:
        from app.services.google.google_service import google_service

        events = await google_service.get_todays_events(
            user_id=current_user["user_id"],
            max_results=max_events
        )

        return JSONResponse(content={
            "message": "Calendar events retrieved successfully",
            "data": events,
            "total": len(events)
        })

    except Exception as e:
        logger.error(f"Error getting calendar events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch calendar events"
        )


@router.get("/email/summary", status_code=status.HTTP_200_OK)
async def get_email_summary(
    max_emails: int = Query(default=5, ge=1, le=20, description="Maximum emails to summarize"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get email summary for the authenticated user.

    Returns unread email count and details of recent unread emails.
    """
    try:
        from app.services.google.google_service import google_service

        summary = await google_service.get_email_summary(
            user_id=current_user["user_id"],
            max_emails=max_emails
        )

        return JSONResponse(content={
            "message": "Email summary retrieved successfully",
            "data": summary
        })

    except Exception as e:
        logger.error(f"Error getting email summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch email summary"
        )


@router.get("/check/google", status_code=status.HTTP_200_OK)
async def check_google_connection(
    current_user: dict = Depends(get_current_user),
):
    """
    Check if the user has a valid Google (Gmail + Calendar) connection.
    """
    try:
        from app.services.google.google_service import google_service

        is_valid = await google_service.check_if_valid_token(current_user["user_id"])

        if is_valid:
            return JSONResponse(content={"connected": True, "message": "Google services connected"})
        else:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"connected": False, "message": "Google services not connected"}
            )

    except Exception as e:
        logger.error(f"Error checking Google connection: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"connected": False, "message": "Google services not connected"}
        )


# Keep backward compatible endpoints that alias to the unified check
@router.get("/check/calendar", status_code=status.HTTP_200_OK)
async def check_calendar_connection(current_user: dict = Depends(get_current_user)):
    """Check Google Calendar connection (alias for /check/google)."""
    return await check_google_connection(current_user)


@router.get("/check/gmail", status_code=status.HTTP_200_OK)
async def check_gmail_connection(current_user: dict = Depends(get_current_user)):
    """Check Gmail connection (alias for /check/google)."""
    return await check_google_connection(current_user)
