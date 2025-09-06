"""
Authentication endpoints
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.auth import Token, UserLogin
from app.services.user_service import UserService
from app.core.database import get_db

router = APIRouter()
logger = get_logger(__name__)


@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user_service = UserService(db)
        user = user_service.authenticate(
            email=form_data.username, password=form_data.password
        )
        
        if not user:
            raise AuthenticationError("Incorrect email or password")
        
        if not user.is_active:
            raise AuthenticationError("Inactive user")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        
        access_token = security.create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
        refresh_token = security.create_refresh_token(
            subject=user.id, expires_delta=refresh_token_expires
        )
        
        logger.info("User logged in successfully", user_id=user.id, email=user.email)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e), email=form_data.username)
        raise AuthenticationError("Login failed")


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    try:
        token_data = security.verify_refresh_token(refresh_token)
        user_service = UserService(db)
        user = user_service.get_by_id(token_data.sub)
        
        if not user or not user.is_active:
            raise AuthenticationError("Invalid refresh token")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
        
        logger.info("Token refreshed successfully", user_id=user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
        
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise AuthenticationError("Invalid refresh token")


@router.post("/logout")
async def logout(
    current_user: User = Depends(security.get_current_user)
) -> Any:
    """
    Logout user (invalidate tokens on client side)
    """
    logger.info("User logged out", user_id=current_user.id)
    return {"message": "Successfully logged out"}


