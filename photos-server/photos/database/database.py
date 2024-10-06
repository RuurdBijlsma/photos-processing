from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from photos.config.app_config import app_config
from photos.database.models import Base


@lru_cache
def get_engine() -> Engine:
    engine = create_engine(app_config.connection_string, echo=False)
    Base.metadata.create_all(engine)
    return engine


@lru_cache
def get_session_maker() -> sessionmaker[Session]:
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_session() -> Generator[Session, None, None]:
    session = get_session_maker()()
    try:
        yield session
    finally:
        session.close()
