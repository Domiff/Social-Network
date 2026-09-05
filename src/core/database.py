from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import func, text, MetaData
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


url = settings.db.DB_URL
engine = create_async_engine(url)
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with new_session() as session:
        yield session


async def ping_database() -> bool:
    try:
        async with new_session() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("Database ping failed", error=str(e))
        return False


SessionDep = Annotated[AsyncSession, Depends(get_session)]
