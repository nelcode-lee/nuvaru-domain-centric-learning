#!/usr/bin/env python3
"""
Production-ready backend for Nuvaru Domain-Centric Learning Platform
Deployed on Railway with Neon DB, AWS S3, and ChromaDB Cloud
"""

import sys
import os
import json
import asyncio
import logging
from pathlib import Path

# Load environment variables from .env file (for local development)
from dotenv import load_dotenv
load_dotenv()

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging for production
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.app.services.simple_document_service import SimpleDocumentService
from backend.app.services.simple_learning_service import SimpleLearningService
from backend.app.database import get_db, init_db
from backend.app.routers.auth import router as auth_router
from backend.app.core.dependencies import get_current_user, get_optional_current_user
from backend.app.models.user import User

app = FastAPI(title="Nuvaru RAG System", version="1.0.0")

# CORS middleware - Production ready
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Initialize database
init_db()

# Initialize services
document_service = SimpleDocumentService()
learning_service = SimpleLearningService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Nuvaru RAG System is running"}

@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    force_upload: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Upload and process a document"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Check file size (10MB limit)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        
        # Determine content type based on file extension if not provided
        content_type = file.content_type
        if not content_type and file.filename:
            if file.filename.lower().endswith('.pdf'):
                content_type = 'application/pdf'
            elif file.filename.lower().endswith('.txt'):
                content_type = 'text/plain'
            elif file.filename.lower().endswith('.md'):
                content_type = 'text/markdown'
            elif file.filename.lower().endswith('.json'):
                content_type = 'application/json'
        
        print(f"📄 Uploading file: {file.filename}, Content-Type: {content_type}, Size: {len(file_content)} bytes")
        
        # Process document
        result = document_service.upload_document(
            file_content=file_content,
            filename=file.filename,
            content_type=content_type,
            metadata={"uploaded_by": current_user.username},
            user_id=current_user.id,
            skip_duplicate_check=force_upload
        )
        
        # Check if it's a duplicate
        if result["status"] == "duplicate":
            duplicate_info = result["duplicate_info"]
            print(f"⚠️ Duplicate detected: {duplicate_info['message']}")
            return JSONResponse(
                content={
                    "message": "Duplicate file detected",
                    "duplicate_info": duplicate_info,
                    "filename": result["filename"],
                    "file_size": len(file_content)
                },
                status_code=409  # Conflict status code
            )
        
        return JSONResponse(content={
            "message": "Document uploaded and processed successfully",
            "doc_id": result["id"],
            "filename": result["filename"],
            "chunks_count": result["chunks_count"],
            "file_size": len(file_content)
        })
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@app.post("/api/v1/learning/chat")
async def chat_with_ai(
    query: str, 
    current_user: User = Depends(get_current_user)
):
    """Chat with AI using RAG"""
    try:
        result = learning_service.chat_with_ai(
            user_id=current_user.id,
            message=query,
            session_id=f"session_{current_user.id}"
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")

@app.get("/api/v1/documents")
async def get_documents(user_id: int = 1, skip: int = 0, limit: int = 10):
    """Get user's documents"""
    try:
        documents = document_service.get_all_documents(
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        
        return JSONResponse(content={
            "documents": documents,
            "total": len(documents)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")

@app.delete("/api/v1/documents/{document_id}")
async def delete_document(document_id: str, user_id: int = 1):
    """Delete a document"""
    try:
        success = document_service.delete_document(
            document_id=document_id,
            user_id=user_id
        )
        
        if success:
            return JSONResponse(content={"message": "Document deleted successfully"})
        else:
            return JSONResponse(content={"message": "Document not found"}, status_code=404)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@app.get("/api/v1/documents/{document_id}/content")
async def get_document_content(document_id: str, user_id: int = 1):
    """Get document content for viewing"""
    try:
        content = document_service.get_document_content(
            document_id=document_id,
            user_id=user_id
        )
        
        if content is not None:
            return JSONResponse(content={"content": content})
        else:
            return JSONResponse(content={"message": "Document not found"}, status_code=404)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document content: {str(e)}")

@app.get("/api/v1/documents/{document_id}/download")
async def download_document(document_id: str, user_id: int = 1):
    """Download document file"""
    try:
        file_data = document_service.get_document_file(
            document_id=document_id,
            user_id=user_id
        )
        
        if file_data is not None:
            from fastapi.responses import Response
            return Response(
                content=file_data["content"],
                media_type=file_data["content_type"],
                headers={
                    "Content-Disposition": f"attachment; filename={file_data['filename']}",
                    "Content-Length": str(file_data["size"])
                }
            )
        else:
            return JSONResponse(content={"message": "Document not found"}, status_code=404)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download document: {str(e)}")

@app.get("/api/v1/learning/stats")
async def get_learning_stats(user_id: int = 1):
    """Get learning statistics"""
    try:
        stats = learning_service.get_knowledge_base_stats(user_id=user_id)
        return JSONResponse(content=stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/api/v1/learning/openai/test")
async def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        result = learning_service.test_openai_connection()
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test OpenAI connection: {str(e)}")

@app.post("/api/v1/learning/openai/configure")
async def configure_openai(
    model: str = None,
    max_tokens: int = None,
    temperature: float = None
):
    """Configure OpenAI parameters"""
    try:
        result = learning_service.configure_openai(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure OpenAI: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    from backend.app.core.config import settings
    
    try:
        # Get port from environment variable (Railway uses PORT)
        port = int(os.getenv("PORT", 8000))
        environment = os.getenv("ENVIRONMENT", "development")
        debug = os.getenv("DEBUG", "false").lower() == "true"
        
        logger.info("🚀 Starting Nuvaru Domain-Centric Learning Platform...")
        logger.info(f"🌍 Environment: {environment}")
        logger.info(f"🐛 Debug Mode: {debug}")
        logger.info(f"🔗 API Documentation: http://localhost:{port}/docs")
        logger.info(f"🌐 Health Check: http://localhost:{port}/health")
        logger.info("📄 PDF Upload Support: ✅ Enabled")
        logger.info("🤖 AI Chat Support: ✅ Enabled")
        logger.info("🔍 Vector Search: ✅ Enabled")
        
        # Production-ready server configuration
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            access_log=True,
            reload=debug
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        sys.exit(1)
