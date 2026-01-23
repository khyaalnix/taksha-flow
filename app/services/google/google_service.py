from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from app.services.oauth import OAuthService
from app.services.google.google_oauth import GoogleAuthBuilder

from app.utils.logger import LoggerFactory
logger = LoggerFactory().get_logger()

# Combined scopes for Google services
GOOGLE_SCOPES = [
    # Gmail scopes
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.labels',
    # Calendar scopes
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar.readonly',
]


class GoogleService:
    """Unified service for Google APIs (Gmail, Calendar) with multi-user support."""

    def __init__(self):
        self.auth_builder = GoogleAuthBuilder()
        self.oauth_service = OAuthService(
            auth_builder=self.auth_builder,
            key_prefix="google",
            refresh_buffer_seconds=300,
            scopes=GOOGLE_SCOPES
        )

    # ==================== OAuth Methods ====================

    async def cache_full_credentials(self, user_id: str, credentials_json: str):
        """Cache full credentials JSON after OAuth callback."""
        return await self.oauth_service.cache_full_credentials(user_id, credentials_json)

    async def check_if_valid_token(self, user_id: str) -> bool:
        """Check if user has valid cached credentials."""
        return await self.oauth_service.check_if_valid_token(user_id)

    async def invalidate_cache(self, user_id: str) -> bool:
        """Invalidate cached credentials for user (used during logout)."""
        return await self.oauth_service.invalidate_cache(user_id)

    # ==================== Gmail Methods ====================

    async def get_gmail_service(self, user_id: str):
        """Build Gmail API service for user."""
        try:
            credentials = await self.oauth_service.get_credentials(user_id)
            service = build('gmail', 'v1', credentials=credentials)
            return service
        except Exception as e:
            logger.error(f"Error building Gmail service for user {user_id}: {e}")
            raise

    async def test_gmail_connection(self, user_id: str):
        """Test Gmail connection for user."""
        try:
            service = await self.get_gmail_service(user_id)
            profile = service.users().getProfile(userId='me').execute()
            logger.info(f"Gmail OAuth working for user {user_id}! Email: {profile.get('emailAddress')}")
            return profile
        except Exception as e:
            logger.error(f"Gmail OAuth test failed for user {user_id}: {e}")
            raise

    async def get_unread_count(self, user_id: str) -> int:
        """Get the count of unread emails in inbox."""
        try:
            service = await self.get_gmail_service(user_id)
            results = service.users().messages().list(
                userId='me',
                q='is:unread in:inbox',
                maxResults=1
            ).execute()
            return results.get('resultSizeEstimate', 0)
        except Exception as e:
            logger.error(f"Error getting unread count for user {user_id}: {e}")
            return 0

    async def get_email_summary(self, user_id: str, max_emails: int = 5) -> dict:
        """Get a summary of recent unread emails."""
        try:
            service = await self.get_gmail_service(user_id)

            # Get unread messages
            results = service.users().messages().list(
                userId='me',
                q='is:unread in:inbox',
                maxResults=max_emails
            ).execute()

            messages = results.get('messages', [])
            total_unread = results.get('resultSizeEstimate', 0)

            if not messages:
                return {
                    'total_unread': 0,
                    'top_sender': None,
                    'top_subject': None,
                    'priority_emails': []
                }

            priority_emails = []
            for msg in messages[:max_emails]:
                msg_data = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = msg_data.get('payload', {}).get('headers', [])
                email_info = {'id': msg['id']}

                for header in headers:
                    name = header.get('name', '').lower()
                    value = header.get('value', '')
                    if name == 'from':
                        # Extract just the name/email
                        if '<' in value:
                            email_info['sender'] = value.split('<')[0].strip().strip('"')
                        else:
                            email_info['sender'] = value.split('@')[0]
                    elif name == 'subject':
                        email_info['subject'] = value[:100]  # Limit subject length
                    elif name == 'date':
                        email_info['date'] = value

                priority_emails.append(email_info)

            # Get top email info
            top_email = priority_emails[0] if priority_emails else {}

            return {
                'total_unread': total_unread,
                'top_sender': top_email.get('sender'),
                'top_subject': top_email.get('subject'),
                'priority_emails': priority_emails
            }

        except Exception as e:
            logger.error(f"Error getting email summary for user {user_id}: {e}")
            return {
                'total_unread': 0,
                'top_sender': None,
                'top_subject': None,
                'priority_emails': []
            }

    async def get_email_priority_item(self, user_id: str) -> Optional[dict]:
        """Get a formatted priority item for emails suitable for the dashboard."""
        try:
            summary = await self.get_email_summary(user_id, max_emails=1)

            if summary['total_unread'] == 0:
                return None

            title = f"{summary['total_unread']} New Email{'s' if summary['total_unread'] != 1 else ''}"
            subtitle = f"Top: {summary['top_subject']}" if summary['top_subject'] else "Check your inbox"

            return {
                'id': 'email_summary',
                'type': 'email',
                'title': title,
                'subtitle': subtitle[:50] + '...' if len(subtitle) > 50 else subtitle
            }

        except Exception as e:
            logger.error(f"Error getting email priority item for user {user_id}: {e}")
            return None

    # ==================== Calendar Methods ====================

    async def get_calendar_service(self, user_id: str):
        """Build Calendar API service for user."""
        try:
            credentials = await self.oauth_service.get_credentials(user_id)
            service = build('calendar', 'v3', credentials=credentials)
            return service
        except Exception as e:
            logger.error(f"Error building Calendar service for user {user_id}: {e}")
            raise

    async def test_calendar_connection(self, user_id: str):
        """Test Calendar connection for user."""
        try:
            service = await self.get_calendar_service(user_id)
            calendar_list = service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            logger.info(f"Calendar OAuth working for user {user_id}! Found {len(calendars)} calendars.")
            return calendars
        except Exception as e:
            logger.error(f"Calendar OAuth test failed for user {user_id}: {e}")
            raise

    async def get_todays_events(self, user_id: str, max_results: int = 10) -> List[dict]:
        """Fetch today's calendar events for a user."""
        try:
            service = await self.get_calendar_service(user_id)

            # Get start and end of today in UTC
            now = datetime.now(timezone.utc)
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)

            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_of_day.isoformat(),
                timeMax=end_of_day.isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            formatted_events = []
            for event in events:
                start = event.get('start', {})
                end = event.get('end', {})

                # Handle all-day events vs timed events
                start_time = start.get('dateTime') or start.get('date')
                end_time = end.get('dateTime') or end.get('date')
                is_all_day = 'date' in start and 'dateTime' not in start

                attendees = event.get('attendees', [])
                attendee_emails = [a.get('email', '') for a in attendees if a.get('email')]

                formatted_events.append({
                    'id': event.get('id', ''),
                    'summary': event.get('summary', 'No Title'),
                    'start_time': start_time,
                    'end_time': end_time,
                    'location': event.get('location'),
                    'attendees': attendee_emails[:5],  # Limit to 5 attendees
                    'is_all_day': is_all_day,
                    'description': event.get('description', '')[:200] if event.get('description') else None
                })

            logger.info(f"Fetched {len(formatted_events)} events for user {user_id}")
            return formatted_events

        except Exception as e:
            logger.error(f"Error fetching calendar events for user {user_id}: {e}")
            return []

    async def get_upcoming_events(self, user_id: str, hours_ahead: int = 24, max_results: int = 5) -> List[dict]:
        """Fetch upcoming events within the specified hours."""
        try:
            service = await self.get_calendar_service(user_id)

            now = datetime.now(timezone.utc)
            end_time = now + timedelta(hours=hours_ahead)

            events_result = service.events().list(
                calendarId='primary',
                timeMin=now.isoformat(),
                timeMax=end_time.isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            formatted_events = []
            for event in events:
                start = event.get('start', {})
                start_time = start.get('dateTime') or start.get('date')

                # Parse the start time to create a nice subtitle
                if start.get('dateTime'):
                    try:
                        dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        time_str = dt.strftime('%I:%M %p').lstrip('0')
                    except:
                        time_str = start_time
                else:
                    time_str = 'All day'

                attendees = event.get('attendees', [])
                attendee_names = []
                for a in attendees[:3]:
                    name = a.get('displayName') or a.get('email', '').split('@')[0]
                    attendee_names.append(name)

                subtitle = time_str
                if attendee_names:
                    subtitle += f" with {', '.join(attendee_names)}"

                formatted_events.append({
                    'id': event.get('id', ''),
                    'title': event.get('summary', 'No Title'),
                    'subtitle': subtitle,
                    'start_time': start_time,
                    'type': 'event'
                })

            return formatted_events

        except Exception as e:
            logger.error(f"Error fetching upcoming events for user {user_id}: {e}")
            return []


# Singleton instance
google_service = GoogleService()
