from datetime import timedelta
from fastapi import APIRouter, Response, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from fastapi_limiter.depends import RateLimiter

from app.client.oauth_client import get_login_url, handle_oauth_callback
from app.core.security import (
    create_access_token,
    get_current_user,
    COOKIE_NAME,
    COOKIE_MAX_AGE,
    COOKIE_SECURE,
    COOKIE_SAMESITE,
    FRONTEND_URL,
    JWT_EXPIRY_DAYS
)
from app.schemas.auth import (
    LoginResponse,
    CallbackResponse,
    UserResponse,
    AuthCheckResponse,
    LogoutResponse,
    UserInfo
)
from app.services.gmail_service import GmailService
from app.services.google_calendar_service import GoogleCalendarService
from app.utils.logger import LoggerFactory
from configs.settings import RATE_LIMITER_CONFIG

logger = LoggerFactory().get_logger()

with open(RATE_LIMITER_CONFIG, "r") as f:
    rate_limiter_config = json.load(f)

router = APIRouter(
            prefix="/auth", tags=["Authentication"], 
            dependencies=[Depends(RateLimiter(**rate)) for rate in rate_limiter_config["auth"]]
        )

gmail_service = GmailService()
google_calendar_service = GoogleCalendarService()


@router.get("/login", response_model=LoginResponse)
async def login():
    try:
        login_url = get_login_url()
        logger.info("Generated OAuth login URL")
        return LoginResponse(
            message="Please visit the auth_url to complete login",
            auth_url=login_url
        )
    except Exception as e:
        logger.error(f"Error generating login URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate login URL"
        )


@router.get("/callback")
async def oauth_callback(code: str):
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required"
        )

    try:
        result = handle_oauth_callback(code)
        user_info = result["user_info"]
        tokens = result["tokens"]
        user_id = user_info['id']

        logger.info(f"OAuth callback successful for user: {user_info.get('email')}")

        await gmail_service.cache_user_token(
            user_id=user_id,
            access_token=tokens["access_token"],
            expires_in=tokens["expiry"],
        )

        await google_calendar_service.cache_user_token(
            user_id=user_id,
            access_token=tokens["access_token"],
            expires_in=tokens["expiry"],
        )

        logger.info(f"Cached OAuth tokens for user: {user_id}")

        jwt_data = {
            "sub": user_id,
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture")
        }

        jwt_token = create_access_token(
            data=jwt_data,
            expires_delta=timedelta(days=JWT_EXPIRY_DAYS)
        )

        # Create redirect response to frontend
        redirect_response = RedirectResponse(url=FRONTEND_URL, status_code=302)

        # Set cookie on the redirect response
        redirect_response.set_cookie(
            key=COOKIE_NAME,
            value=jwt_token,
            max_age=COOKIE_MAX_AGE,
            path="/",
            httponly=True,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE
        )

        logger.info(f"JWT token created and set in cookie for user: {user_id}, redirecting to frontend")

        return redirect_response

    except Exception as e:
        logger.error(f"Error during OAuth callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)


@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]

        await gmail_service.invalidate_cache(user_id)
        await google_calendar_service.invalidate_cache(user_id)

        logger.info(f"Invalidated cached tokens for user: {user_id}")

        response.delete_cookie(
            key=COOKIE_NAME,
            path="/",
            httponly=True,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE
        )

        logger.info(f"User logged out successfully: {user_id}")

        return LogoutResponse(message="Logout successful")

    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/check", response_model=AuthCheckResponse)
async def check_auth(current_user: dict = Depends(get_current_user)):
    return AuthCheckResponse(
        authenticated=True,
        user=UserResponse(**current_user)
    )
