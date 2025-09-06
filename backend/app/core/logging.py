"""
Structured logging configuration for the Nuvaru platform
"""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory


def setup_logging() -> None:
    """Configure structured logging for the application"""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


class SecurityFilter:
    """Filter to remove sensitive information from logs"""
    
    SENSITIVE_KEYS = {
        "password", "token", "secret", "key", "authorization",
        "cookie", "session", "api_key", "access_token", "refresh_token"
    }
    
    @classmethod
    def filter_sensitive_data(cls, logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from log events"""
        filtered_dict = {}
        
        for key, value in event_dict.items():
            if any(sensitive_key in key.lower() for sensitive_key in cls.SENSITIVE_KEYS):
                filtered_dict[key] = "[REDACTED]"
            elif isinstance(value, dict):
                filtered_dict[key] = cls.filter_sensitive_data(logger, method_name, value)
            else:
                filtered_dict[key] = value
                
        return filtered_dict


