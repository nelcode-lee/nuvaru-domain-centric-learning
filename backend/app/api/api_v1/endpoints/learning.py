"""
Learning engine endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.exceptions import LLMError, ValidationError
from app.core.logging import get_logger
from app.models.user import User
from app.services.production_learning_service import ProductionLearningService as LearningService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/chat", response_model=dict)
async def chat_with_ai(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    message: str = Form(...),
    knowledge_base_id: Optional[str] = Form(None),
    context: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
) -> dict:
    """Chat with the AI assistant using RAG"""
    try:
        learning_service = LearningService()
        
        response = learning_service.chat_with_ai(
            message=message,
            user_id=current_user.id,
            knowledge_base_id=knowledge_base_id,
            context=context,
            session_id=session_id
        )
        
        logger.info(
            "AI chat completed successfully",
            user_id=current_user.id,
            session_id=response.get("session_id"),
            message_length=len(message)
        )
        
        return response
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to process AI chat", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process AI chat"
        )


@router.post("/feedback", response_model=dict)
async def submit_feedback(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    session_id: str = Form(...),
    response_id: str = Form(...),
    rating: int = Form(...),
    feedback: str = Form(...),
    correctness: bool = Form(...),
) -> dict:
    """Submit learning feedback for improvement"""
    try:
        # Validate rating
        if not 1 <= rating <= 5:
            raise ValidationError("Rating must be between 1 and 5")
        
        learning_service = LearningService()
        
        result = learning_service.submit_feedback(
            session_id=session_id,
            response_id=response_id,
            rating=rating,
            feedback=feedback,
            correctness=correctness,
            user_id=current_user.id
        )
        
        logger.info(
            "Feedback submitted successfully",
            user_id=current_user.id,
            session_id=session_id,
            rating=rating
        )
        
        return result
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to submit feedback", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )


@router.get("/sessions", response_model=List[dict])
async def get_learning_sessions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
) -> List[dict]:
    """Get learning sessions for the current user"""
    try:
        learning_service = LearningService()
        
        sessions = learning_service.get_learning_sessions(
            user_id=current_user.id,
            limit=limit
        )
        
        logger.info(
            "Learning sessions retrieved successfully",
            user_id=current_user.id,
            count=len(sessions)
        )
        
        return sessions
        
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to get learning sessions", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get learning sessions"
        )


@router.get("/stats", response_model=dict)
async def get_knowledge_base_stats(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    knowledge_base_id: Optional[str] = None,
) -> dict:
    """Get knowledge base statistics"""
    try:
        learning_service = LearningService()
        
        stats = learning_service.get_knowledge_base_stats(
            user_id=current_user.id,
            knowledge_base_id=knowledge_base_id
        )
        
        logger.info(
            "Knowledge base stats retrieved successfully",
            user_id=current_user.id
        )
        
        return stats
        
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to get knowledge base stats", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get knowledge base stats"
        )


@router.post("/improve", response_model=dict)
async def improve_knowledge_base(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    knowledge_base_id: str = Form(...),
    feedback_data: List[dict] = Form(...),
) -> dict:
    """Improve knowledge base based on feedback"""
    try:
        learning_service = LearningService()
        
        result = learning_service.improve_knowledge_base(
            user_id=current_user.id,
            knowledge_base_id=knowledge_base_id,
            feedback_data=feedback_data
        )
        
        logger.info(
            "Knowledge base improvement initiated",
            user_id=current_user.id,
            knowledge_base_id=knowledge_base_id
        )
        
        return result
        
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to improve knowledge base", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to improve knowledge base"
        )
