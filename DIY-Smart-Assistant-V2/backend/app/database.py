"""
Database Configuration
SQLAlchemy setup for async database operations
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData

from .config import settings

# Create async engine
if settings.database_url.startswith("sqlite"):
    # SQLite for development
    engine = create_async_engine(
        settings.database_url.replace("sqlite://", "sqlite+aiosqlite://"),
        echo=settings.debug,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL for production
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=settings.debug,
        pool_pre_ping=True,
        pool_recycle=300,
    )

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Metadata for table creation
metadata = MetaData()


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create database tables"""
    from .models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all database tables"""
    from .models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)