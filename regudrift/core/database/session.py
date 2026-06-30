from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from regudrift.config.settings import settings

# Create highly configured asynchronous SQLAlchemy Engine
# sqlite+aiosqlite works locally out of the box. Postgres/MySQL async drivers are fully compatible.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

# Async session factory creation
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection provider returning an active asynchronous SQLAlchemy session.
    Automatically handles commit rollback operations and clean session closing.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
