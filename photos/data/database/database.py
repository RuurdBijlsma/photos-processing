from __future__ import annotations

from collections.abc import Generator
from contextlib import asynccontextmanager
from typing import Annotated

from async_lru import alru_cache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from photos.config.app_config import app_config


class Base(AsyncAttrs, DeclarativeBase):
    pass


@alru_cache
async def get_engine() -> AsyncEngine:
    engine = create_async_engine(app_config.connection_string, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


@alru_cache
async def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=await get_engine())


@asynccontextmanager
async def get_session() -> AsyncSession:
    session = (await get_session_maker())()
    try:
        yield session
    finally:
        await session.close()


async def _session_dependency() -> Generator[AsyncSession, None, None]:
    async with get_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(_session_dependency)]
