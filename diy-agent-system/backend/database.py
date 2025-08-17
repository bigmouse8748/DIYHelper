"""
Database configuration and connection management
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # Use SQLite for local development
    "sqlite:///./diy_assistant.db"
)

logger.info(f"Database URL configured: {DATABASE_URL.replace(os.getenv('DB_PASSWORD', ''), '***')}")

# Create engine with different settings for SQLite vs PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL debugging
        connect_args={"check_same_thread": False}  # SQLite specific
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        echo=False  # Set to True for SQL debugging
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    logger.info("Creating database tables...")
    # Import here to avoid circular imports
    from models.user_models import Base
    from models.product_models import ProductRecommendation  # Import to register table
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

def test_connection():
    """Test database connection"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            if DATABASE_URL.startswith("sqlite"):
                result = connection.execute(text("SELECT sqlite_version();"))
                version = result.fetchone()[0]
                logger.info(f"Database connection successful. SQLite version: {version}")
            else:
                result = connection.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                logger.info(f"Database connection successful. PostgreSQL version: {version}")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False