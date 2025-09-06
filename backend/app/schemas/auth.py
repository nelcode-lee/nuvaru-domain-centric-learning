"""
Authentication schemas
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: Optional[dict] = None


class TokenPayload(BaseModel):
    """Token payload schema"""
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None


class PasswordReset(BaseModel):
    """Password reset schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str


class ChangePassword(BaseModel):
    """Change password schema"""
    current_password: str
    new_password: str



