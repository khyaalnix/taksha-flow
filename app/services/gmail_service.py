from googleapiclient.discovery import build
from app.services.oauth import OAuthService
from app.services.google_oauth import GoogleAuthBuilder, GMAIL_SCOPES

from app.utils.logger import LoggerFactory
logger = LoggerFactory.get_logger()



class GmailService:
    """Service for managing Gmail API operations with multi-user support."""

    def __init__(self):
        self.auth_builder = GoogleAuthBuilder()
        self.oauth_service = OAuthService(
            auth_builder=self.auth_builder,
            key_prefix="gmail",
            refresh_buffer_seconds=300,
            scopes=GMAIL_SCOPES
        )

    async def get_gmail_service(self, user_id: str):
        try:
            credentials = await self.oauth_service.get_credentials(user_id)
            service = build('gmail', 'v1', credentials=credentials)
            return service
        except Exception as e:
            logger.error(f"Error building Gmail service for user {user_id}: {e}")
            raise

    async def cache_user_token(self, user_id: str, access_token: str, expires_in: str):

        return await self.oauth_service.cache_user_token(user_id, access_token, expires_in)

    async def check_if_valid_token(self, user_id: str) -> bool:

        return await self.oauth_service.check_if_valid_token(user_id)

    async def invalidate_cache(self, user_id: str) -> bool:

        return await self.oauth_service.invalidate_cache(user_id)

    async def test_connection(self, user_id: str):
        
        try:
            service = await self.get_gmail_service(user_id)
            profile = service.users().getProfile(userId='me').execute()
            logger.info(f"OAuth working for user {user_id}! Email: {profile.get('emailAddress')}")
            return profile
        except Exception as e:
            logger.error(f"OAuth test failed for user {user_id}: {e}")
            raise
