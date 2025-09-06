"""
User models for authentication
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Profile information
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Preferences
    preferred_language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")

class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    bio: Optional[str] = None

class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None

class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: str
    timezone: str
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """User login schema"""
    username: str  # Can be username or email
    password: str

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None