from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.fastapi_quickstart.core.config import settings

DB_ECHO = settings.ENVIRONMENT == "development"  # Enable SQL logs in development

if settings.DB_TYPE == "postgres":
    async_engine = create_async_engine(
        str(settings.ASYNC_DATABASE_URI),
        echo=DB_ECHO,
        future=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.MAX_OVERFLOW,
    )
elif settings.DB_TYPE == "sqlite":
    async_engine = create_async_engine(
        str(settings.ASYNC_DATABASE_URI),
        echo=DB_ECHO,
        future=True,
        connect_args={"check_same_thread": False},
    )
else:
    err_msg = "Unsupported DB_TYPE: {settings.DB_TYPE}"
    raise ValueError(err_msg)

# Session factory
async_session_factory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a new async session for each request.
    """
    async with async_session_factory() as async_session:
        yield async_session
