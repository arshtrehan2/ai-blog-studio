from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

Base = declarative_base()

_sync_engine = None
_async_engine = None
_AsyncSessionLocal = None


def get_sync_engine():
    """Get or create sync engine (used by Alembic)."""
    global _sync_engine
    if _sync_engine is None:
        url = settings.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        _sync_engine = create_engine(url, pool_pre_ping=True)
    return _sync_engine


def get_async_engine():
    """Get or create async engine."""
    global _async_engine
    if _async_engine is None:
        url = settings.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("sqlite://"):
            url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        _async_engine = create_async_engine(
            url,
            pool_pre_ping=True,
            echo=settings.DEBUG,
        )
    return _async_engine


def get_session_factory():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _AsyncSessionLocal


async def get_db() -> AsyncSession:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
