#!/usr/bin/env python3
"""
Minimal Railway backend for Nuvaru Platform
Ultra-simplified for guaranteed deployment
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    allow_origins=["*"],
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
            "authentication": "coming_soon",
            "document_processing": "coming_soon",
            "vector_search": "coming_soon",
            "ai_chat": "coming_soon"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting Nuvaru backend on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )