"""
Password utilities for hashing and verification
"""

from passlib.context import CryptContext
from passlib.hash import bcrypt

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def check_password_strength(password: str) -> dict:
    """Check password strength and return validation results"""
    result = {
        "is_valid": True,
        "score": 0,
        "issues": []
    }
    
    # Length check
    if len(password) < 8:
        result["is_valid"] = False
        result["issues"].append("Password must be at least 8 characters long")
    else:
        result["score"] += 1
    
    # Uppercase check
    if not any(c.isupper() for c in password):
        result["issues"].append("Password should contain at least one uppercase letter")
    else:
        result["score"] += 1
    
    # Lowercase check
    if not any(c.islower() for c in password):
        result["issues"].append("Password should contain at least one lowercase letter")
    else:
        result["score"] += 1
    
    # Number check
    if not any(c.isdigit() for c in password):
        result["issues"].append("Password should contain at least one number")
    else:
        result["score"] += 1
    
    # Special character check
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        result["issues"].append("Password should contain at least one special character")
    else:
        result["score"] += 1
    
    # Common password check
    common_passwords = [
        "password", "123456", "123456789", "qwerty", "abc123",
        "password123", "admin", "letmein", "welcome", "monkey"
    ]
    if password.lower() in common_passwords:
        result["is_valid"] = False
        result["issues"].append("Password is too common")
    
    return result