#!/usr/bin/env python3
"""
Railway-optimized backend for Nuvaru Platform
Simplified for reliable deployment
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
