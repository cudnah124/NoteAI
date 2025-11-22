"""
Database configuration and session management
Handles SQLAlchemy async engine and session factory
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

logger = logging.getLogger(__name__)

# Validate DATABASE_URL
if not settings.DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set!")
    raise ValueError("DATABASE_URL is required. Please set it in your environment variables.")

# Log connection attempt (hide password)
masked_url = settings.DATABASE_URL
if "@" in masked_url:
    parts = masked_url.split("@")
    if ":" in parts[0]:
        user_pass = parts[0].split("://")[-1]
        user = user_pass.split(":")[0]
        masked_url = masked_url.replace(user_pass, f"{user}:****")
logger.info(f"Connecting to database: {masked_url}")

# Convert postgresql:// to postgresql+asyncpg:// for async support
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine with connection pool settings
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,  # Test connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency for getting async database session
    Automatically handles commit/rollback
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    try:
        logger.info("Attempting to connect to database...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.error("Please check DATABASE_URL environment variable")
        raise
