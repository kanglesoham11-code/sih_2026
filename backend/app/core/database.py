"""
ORCA Database Configuration
PostgreSQL with PostGIS support
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from loguru import logger

from app.core.config import settings
from app.models.base import Base

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.is_development,
    poolclass=NullPool if settings.is_development else None,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """Dependency for getting database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create tables"""
    logger.info("Initializing database...")
    
    # Import all models to register them with Base.metadata
    import app.models.users
    import app.models.sources
    import app.models.datasets
    import app.models.observations
    import app.models.forecasts
    import app.models.warnings
    import app.models.pfz_zones
    import app.models.boundaries
    import app.models.recommendations
    import app.models.audit
    
    from sqlalchemy import text
    
    async with engine.begin() as conn:
        # Enable PostGIS extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology"))
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialized successfully")


async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")
