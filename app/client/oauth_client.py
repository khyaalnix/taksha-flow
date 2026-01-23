from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import requests
import os

from configs.settings import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
)



SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
]

class GoogleOAuthClient:
    def get_auth_url(self):
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URI,
        )

        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return auth_url

    
    def exchange_code_for_token(self, code):
        import os
        # Disable oauthlib's strict token validation
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URI,
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials

        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {credentials.token}"},
        ).json()

        return credentials, user_info


oauth_client = GoogleOAuthClient()

def get_login_url():
    return oauth_client.get_auth_url()

def handle_oauth_callback(code: str):
    from datetime import timezone, datetime
    creds, user_info = oauth_client.exchange_code_for_token(code)

    # Convert expiry to timestamp in milliseconds
    # If expiry is naive, treat it as UTC
    if creds.expiry:
        if creds.expiry.tzinfo is None:
            # Naive datetime - assume it's UTC
            expiry_utc = creds.expiry.replace(tzinfo=timezone.utc)
        else:
            expiry_utc = creds.expiry

        expiry_timestamp = int(expiry_utc.timestamp() * 1000)
    else:
        expiry_timestamp = None

    return {
        "tokens": {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "expiry": expiry_timestamp,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
        },
        "credentials_json": creds.to_json(),  # Full credentials for caching
        "user_info": user_info,
    }

