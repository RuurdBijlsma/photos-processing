from __future__ import annotations

from collections.abc import Generator
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

from async_lru import alru_cache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

from photos.config.app_config import app_config
from photos.data.models.image_models import Base


@alru_cache
async def get_engine() -> AsyncEngine:
    return create_async_engine(app_config.connection_string, echo=False)


@alru_cache
async def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=await get_engine())


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = (await get_session_maker())()
    try:
        yield session
    finally:
        await session.close()


async def _session_dependency() -> Generator[AsyncSession, None, None]:
    async with get_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(_session_dependency)]
