from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.credentials import TokenState

from app.services.oauth import OAuthService, AuthBuilder
from app.utils.logger import LoggerFactory
logger = LoggerFactory().get_logger()

GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.labels'
]

CALENDAR_SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar.readonly'
]

class GoogleAuthBuilder(AuthBuilder):

    def build_creds_from_token(self, token_data, scopes: list[str]):
        """Build credentials from token data (can be dict or JSON string)."""
        try:
            import json
            # Handle both dict (from Redis cache) and string (JSON) inputs
            if isinstance(token_data, dict):
                info = token_data
            elif isinstance(token_data, str):
                info = json.loads(token_data)
            else:
                raise ValueError(f"Unexpected token_data type: {type(token_data)}")

            creds = Credentials.from_authorized_user_info(info, scopes=scopes)
            return creds
        except Exception as e:
            logger.error(f"Error building credentials from token JSON: {e}")
            raise ValueError(f"Failed to build credentials from token JSON: {e}")

    def build_creds_from_access_token(self,access_token: str,expires_in: str,scopes: list[str]):
        try:
            # Use naive UTC to avoid naive/aware comparison issues inside google library
            expiry = datetime.utcfromtimestamp(int(expires_in)//1000)
            creds = Credentials(token=access_token, expiry=expiry,scopes=scopes)
            logger.info("Successfully built credentials from provided access token.")
            return creds

        except Exception as e:
            logger.error(f"Error building credentials from access token: {e}")
            raise ValueError(f"Failed to build credentials from access token: {e}")
    
    def refresh_or_create(self,existing_token = None, scopes: list[str] = None):
        try:
            if existing_token and hasattr(existing_token, 'refresh_token') and existing_token.refresh_token:
                if existing_token.token_state != TokenState.FRESH:
                    existing_token.refresh(Request())
                    logger.info("Token refreshed successfully")
                    return existing_token
                else:
                    return existing_token

            if existing_token:
                if existing_token.valid:
                    logger.info("Existing token (without refresh_token) is still valid")
                    return existing_token
                else:
                    logger.error("Existing token has expired and cannot be refreshed (no refresh_token)")
                    raise RuntimeError(
                        "Token has expired and cannot be refreshed. "
                        "No refresh_token available. Please provide new oauth-token and oauth-token-expiry."
                    )

            # No existing creds available: do not attempt local flows by default.
            # Require caller to provide fresh oauth-token via headers.
            logger.error("No existing credentials available to refresh or create.")
            raise RuntimeError(
                "No credentials available in cache. Please provide oauth-token and oauth-token-expiry headers."
            )

        except Exception as e:
            logger.error(f"Error in refresh_or_create: {e}")
            raise RuntimeError(f"Failed to refresh or create credentials: {e}")


    def is_valid(self, creds, refresh_buffer_seconds: int = 300) -> bool:
        if creds is None:
            return False

        try:
            if not hasattr(creds, "token_state"):
                return False 
            return creds.token_state == TokenState.FRESH
            
        except Exception as e:
            logger.error(f"Error checking credential validity: {e}")
            return False

    def ttl(self, creds, refresh_buffer_seconds: int = 1800) -> int:
        try:
            expiry = getattr(creds, "expiry", None)
            if not expiry:
                return 3600
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            current_time = datetime.now(timezone.utc)
            seconds_until_expiry = (expiry - current_time).total_seconds()
            ttl = int(seconds_until_expiry) - refresh_buffer_seconds
            return max(60, ttl)

        except Exception as e:
                logger.error(f"Error computing TTL: {e}")
                return 3600
        
    def to_json(self,credentials):
        try:
            return credentials.to_json()
        except Exception as e:
            logger.error(f"Unable to convert credentials/token to json: {str(e)}")
            raise e
