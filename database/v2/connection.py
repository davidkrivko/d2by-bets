from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from config import (
    DB2_USER,
    DB2_PASSWORD,
    DB2_HOST,
    DB2_PORT,
    DB2_NAME,
)


DB_STRING = f"postgresql+asyncpg://{DB2_USER}:{DB2_PASSWORD}@{DB2_HOST}:{DB2_PORT}/{DB2_NAME}"
db_2 = create_async_engine(DB_STRING, pool_size=10, max_overflow=20)
meta_2 = MetaData()

async_session_2 = async_sessionmaker(
    bind=db_2, class_=AsyncSession, expire_on_commit=False, autocommit=False
)
