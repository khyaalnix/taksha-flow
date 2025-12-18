from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginResponse(BaseModel):
    message: str
    auth_url: str


class UserInfo(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    verified_email: Optional[bool] = None


class CallbackResponse(BaseModel):
    message: str
    user: UserInfo


class UserResponse(BaseModel):
    user_id: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None


class AuthCheckResponse(BaseModel):
    authenticated: bool
    user: UserResponse


class LogoutResponse(BaseModel):
    message: str


class TokenData(BaseModel):
    sub: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
