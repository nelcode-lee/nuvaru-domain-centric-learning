#!/usr/bin/env python3
"""
Railway-optimized backend for Nuvaru Platform
Simplified for reliable deployment
"""

import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Nuvaru RAG System",
    version="1.0.0",
    description="Domain-Centric Learning Platform"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple user models for demo
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: Optional[dict] = None

# Simple in-memory user storage (for demo purposes)
users_db = {}

@app.post("/auth/register", response_model=dict)
async def register(user_data: UserCreate):
    """Register a new user"""
    if user_data.username in users_db:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Simple user creation (in production, use proper password hashing)
    users_db[user_data.username] = {
        "id": len(users_db) + 1,
        "email": user_data.email,
        "username": user_data.username,
        "password": user_data.password,  # In production, hash this
        "full_name": user_data.full_name,
        "is_active": True
    }
    
    return {
        "id": users_db[user_data.username]["id"],
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "is_active": True
    }

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user and return access token"""
    user = users_db.get(user_credentials.username)
    
    if not user or user["password"] != user_credentials.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if not user["is_active"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Simple token (in production, use proper JWT)
    access_token = f"demo_token_{user['id']}_{user['username']}"
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=30,
        user={
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user["full_name"]
        }
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Nuvaru Domain-Centric Learning Platform",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "nuvaru-backend",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "nuvaru-rag-api",
        "status": "operational",
        "features": {
            "authentication": "enabled",
            "document_processing": "enabled",
            "vector_search": "enabled",
            "ai_chat": "enabled"
        }
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "message": "API is working!",
        "environment_variables": {
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "database_configured": bool(os.getenv("NEON_DATABASE_URL")),
            "s3_configured": bool(os.getenv("AWS_ACCESS_KEY_ID")),
            "chromadb_configured": bool(os.getenv("CHROMA_API_KEY"))
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting Nuvaru backend on port {port}")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        raise
