"""
Custom exceptions for the Nuvaru platform
"""

from typing import Any, Dict, Optional


class NuvaruException(Exception):
    """Base exception for Nuvaru platform"""
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        super().__init__(detail)


class AuthenticationError(NuvaruException):
    """Authentication related errors"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail=detail, status_code=401, error_code="AUTHENTICATION_ERROR")


class AuthorizationError(NuvaruException):
    """Authorization related errors"""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail=detail, status_code=403, error_code="AUTHORIZATION_ERROR")


class ValidationError(NuvaruException):
    """Data validation errors"""
    
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(detail=detail, status_code=422, error_code="VALIDATION_ERROR")


class NotFoundError(NuvaruException):
    """Resource not found errors"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=404, error_code="NOT_FOUND_ERROR")


class ConflictError(NuvaruException):
    """Resource conflict errors"""
    
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(detail=detail, status_code=409, error_code="CONFLICT_ERROR")


class RateLimitError(NuvaruException):
    """Rate limiting errors"""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(detail=detail, status_code=429, error_code="RATE_LIMIT_ERROR")


class DatabaseError(NuvaruException):
    """Database related errors"""
    
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(detail=detail, status_code=500, error_code="DATABASE_ERROR")


class VectorDatabaseError(NuvaruException):
    """Vector database related errors"""
    
    def __init__(self, detail: str = "Vector database operation failed"):
        super().__init__(detail=detail, status_code=500, error_code="VECTOR_DATABASE_ERROR")


class LLMError(NuvaruException):
    """LLM related errors"""
    
    def __init__(self, detail: str = "LLM operation failed"):
        super().__init__(detail=detail, status_code=500, error_code="LLM_ERROR")


class LearningEngineError(NuvaruException):
    """Learning engine related errors"""
    
    def __init__(self, detail: str = "Learning engine operation failed"):
        super().__init__(detail=detail, status_code=500, error_code="LEARNING_ENGINE_ERROR")


class FileProcessingError(NuvaruException):
    """File processing related errors"""
    
    def __init__(self, detail: str = "File processing failed"):
        super().__init__(detail=detail, status_code=500, error_code="FILE_PROCESSING_ERROR")


class ConfigurationError(NuvaruException):
    """Configuration related errors"""
    
    def __init__(self, detail: str = "Configuration error"):
        super().__init__(detail=detail, status_code=500, error_code="CONFIGURATION_ERROR")


