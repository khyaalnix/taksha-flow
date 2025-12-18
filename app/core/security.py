import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import Cookie, HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError

from app.utils.logger import LoggerFactory

logger = LoggerFactory().get_logger()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"
COOKIE_NAME = "taksha_flow_token"
COOKIE_MAX_AGE = 30 * 24 * 60 * 60
JWT_EXPIRY_DAYS = 30

# Environment-based security settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT.lower() == "production"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", str(IS_PRODUCTION)).lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "none" if IS_PRODUCTION else "lax")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if not data.get("sub") or not data.get("email"):
        raise ValueError("Token data must include 'sub' and 'email'")

    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(days=JWT_EXPIRY_DAYS))

    to_encode.update({
        "exp": expire,
        "iat": now
    })

    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"JWT token created for user: {data.get('email')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating JWT token: {str(e)}")
        raise


def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        logger.warning("Attempted access with expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_current_user(token: Optional[str] = Cookie(None, alias=COOKIE_NAME)) -> Dict[str, Any]:
    if not token:
        logger.warning("Request without authentication token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please login.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    payload = decode_token(token)
    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id or not email:
        logger.error("Token missing required fields")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    return {
        "user_id": user_id,
        "email": email,
        "name": payload.get("name"),
        "picture": payload.get("picture")
    }


def verify_token(token: str) -> bool:
    try:
        decode_token(token)
        return True
    except HTTPException:
        return False
