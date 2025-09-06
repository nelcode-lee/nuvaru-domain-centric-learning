"""
Main API router for version 1
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, documents, knowledge, learning, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


