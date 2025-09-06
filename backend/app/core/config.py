"""
Configuration management for the Nuvaru platform
"""

from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
import secrets
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app configuration
    PROJECT_NAME: str = "Nuvaru Domain-Centric Learning Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    ALGORITHM: str = "HS256"
    
    # CORS and hosts
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    ALLOWED_HOSTS: List[str] = ["*"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database configuration
    DATABASE_URL: Optional[str] = None
    NEON_DATABASE_URL: Optional[str] = None
    
    # Vector database configuration (ChromaDB)
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_NAME: str = "nuvaru_knowledge"
    CHROMA_PERSIST_DIRECTORY: Optional[str] = None  # For persistent storage
    CHROMA_AUTH_TOKEN: Optional[str] = None  # For ChromaDB Cloud
    CHROMA_API_URL: Optional[str] = None  # For ChromaDB Cloud
    
    # Ollama configuration
    OLLAMA_HOST: str = "localhost"
    OLLAMA_PORT: int = 11434
    OLLAMA_MODEL: str = "llama2:7b"
    
    # Redis configuration (for caching and sessions)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Email configuration
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Monitoring and logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    
    # File storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None  # For custom S3-compatible services
    
    # Railway Configuration
    RAILWAY_ENVIRONMENT: Optional[str] = None
    RAILWAY_PROJECT_ID: Optional[str] = None
    RAILWAY_SERVICE_ID: Optional[str] = None
    PORT: int = 8000  # Railway uses PORT environment variable
    
    # AI and ML configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    MAX_CONTEXT_LENGTH: int = 4096
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # OpenAI configuration
    OPENAI_API_KEY: Optional[str] = None
    
    # Learning engine configuration
    LEARNING_RATE: float = 0.001
    BATCH_SIZE: int = 32
    MAX_EPOCHS: int = 100
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Changed from "allow" to "ignore" to handle extra env vars gracefully


# Create settings instance
settings = Settings()

# Override with environment variables if present
if os.getenv("DATABASE_URL"):
    settings.DATABASE_URL = os.getenv("DATABASE_URL")

if os.getenv("NEON_DATABASE_URL"):
    settings.NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL")
    settings.DATABASE_URL = settings.NEON_DATABASE_URL
