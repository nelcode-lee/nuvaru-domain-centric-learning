"""
Document management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.exceptions import FileProcessingError, ValidationError
from app.core.logging import get_logger
from app.models.user import User
from app.services.simple_document_service import SimpleDocumentService as DocumentService

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=List[dict])
async def get_documents(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 100,
    knowledge_base_id: Optional[str] = None,
) -> List[dict]:
    """Get user documents"""
    try:
        document_service = DocumentService()
        documents = document_service.get_user_documents(
            user_id=current_user.id,
            limit=limit
        )
        
        return documents
        
    except Exception as e:
        logger.error("Failed to get documents", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )


@router.post("/upload", response_model=dict)
async def upload_document(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    knowledge_base_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
) -> dict:
    """Upload a new document"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Prepare metadata
        metadata = {
            "knowledge_base_id": knowledge_base_id,
            "description": description,
            "original_filename": file.filename,
        }
        
        # Process document
        document_service = DocumentService()
        result = document_service.upload_document(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type,
            metadata=metadata,
            user_id=current_user.id
        )
        
        logger.info(
            "Document uploaded successfully",
            doc_id=result["id"],
            filename=file.filename,
            user_id=current_user.id
        )
        
        return result
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except FileProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to upload document", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.get("/{document_id}", response_model=dict)
async def get_document(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    document_id: str,
) -> dict:
    """Get specific document"""
    try:
        document_service = DocumentService()
        document = document_service.get_document(
            doc_id=document_id,
            user_id=current_user.id
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get document", error=str(e), doc_id=document_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document"
        )


@router.delete("/{document_id}")
async def delete_document(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    document_id: str,
) -> dict:
    """Delete a document"""
    try:
        document_service = DocumentService()
        success = document_service.delete_document(
            doc_id=document_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete document", error=str(e), doc_id=document_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.post("/search", response_model=List[dict])
async def search_documents(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    query: str = Form(...),
    knowledge_base_id: Optional[str] = Form(None),
    limit: int = Form(10),
) -> List[dict]:
    """Search documents using vector similarity"""
    try:
        document_service = DocumentService()
        results = document_service.search_documents(
            query=query,
            user_id=current_user.id,
            knowledge_base_id=knowledge_base_id,
            limit=limit
        )
        
        return results
        
    except Exception as e:
        logger.error("Failed to search documents", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search documents"
        )
