"""
User management endpoints
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_current_superuser
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.auth import UserRegister, ChangePassword
from app.services.user_service import UserService

router = APIRouter()
logger = get_logger(__name__)


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "company": current_user.company,
        "role": current_user.role,
        "department": current_user.department,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login,
    }


@router.put("/me", response_model=dict)
async def update_current_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    full_name: str = None,
    company: str = None,
    role: str = None,
    department: str = None,
) -> Any:
    """Update current user information"""
    try:
        user_service = UserService(db)
        updated_user = user_service.update(
            current_user.id,
            full_name=full_name,
            company=company,
            role=role,
            department=department,
        )
        
        return {
            "id": updated_user.id,
            "email": updated_user.email,
            "username": updated_user.username,
            "full_name": updated_user.full_name,
            "company": updated_user.company,
            "role": updated_user.role,
            "department": updated_user.department,
        }
        
    except Exception as e:
        logger.error("Failed to update user", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user information"
        )


@router.post("/change-password")
async def change_password(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    password_data: ChangePassword,
) -> Any:
    """Change user password"""
    try:
        user_service = UserService(db)
        user_service.change_password(
            current_user.id,
            password_data.current_password,
            password_data.new_password,
        )
        
        return {"message": "Password changed successfully"}
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to change password", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/register", response_model=dict)
async def register_user(
    *,
    db: Session = Depends(get_db),
    user_data: UserRegister,
) -> Any:
    """Register a new user"""
    try:
        user_service = UserService(db)
        user = user_service.create(user_data)
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "company": user.company,
            "role": user.role,
            "department": user.department,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
        }
        
    except Exception as e:
        logger.error("Failed to register user", error=str(e), email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[dict])
async def get_users(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Get all users (superuser only)"""
    try:
        user_service = UserService(db)
        users = user_service.get_all(skip=skip, limit=limit)
        
        return [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "company": user.company,
                "role": user.role,
                "department": user.department,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at,
                "last_login": user.last_login,
            }
            for user in users
        ]
        
    except Exception as e:
        logger.error("Failed to get users", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )



