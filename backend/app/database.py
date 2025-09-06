"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from backend.app.core.config import settings
from backend.app.models.user import Base

# Database URL - use Neon DB in production, SQLite for development
if settings.NEON_DATABASE_URL:
    DATABASE_URL = settings.NEON_DATABASE_URL
else:
    DATABASE_URL = "sqlite:///./nuvaru.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def init_db():
    """Initialize database with default data"""
    create_tables()
    
    # Create default admin user if no users exist
    db = SessionLocal()
    try:
        from backend.app.services.user_service import UserService
        from backend.app.models.user import UserCreate
        
        user_service = UserService(db)
        existing_users = user_service.get_all_users()
        
        if not existing_users:
            # Create default admin user
            admin_user = UserCreate(
                email="admin@nuvaru.com",
                username="admin",
                password="Admin123!@#",
                full_name="System Administrator",
                bio="Default system administrator account"
            )
            
            try:
                admin = user_service.create_user(admin_user)
                # Make admin a superuser
                admin_user_db = user_service.get_user_by_id(admin.id)
                admin_user_db.is_superuser = True
                db.commit()
                print("✅ Default admin user created: admin@nuvaru.com / Admin123!@#")
            except Exception as e:
                print(f"⚠️ Could not create default admin user: {e}")
        
    finally:
        db.close()

