from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from config import (
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
    DB_NAME,
)


DB_STRING = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
db = create_async_engine(DB_STRING, pool_size=10, max_overflow=20)
meta = MetaData()

async_session = async_sessionmaker(
    bind=db, class_=AsyncSession, expire_on_commit=False, autocommit=False
)
