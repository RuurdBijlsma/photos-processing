import logging
import multiprocessing
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from photos.config.app_config import app_config
from photos.data.database.database import get_session
from photos.data.database.db_utils import add_user
from photos.data.database.migrations import migrate_db
from photos.data.models.media_model import Role
from photos.processing.collection_processing.process_all import process_all
from photos.processing.watch.watch_for_changes import watch_files
from photos.server.host_thumbnails import host_thumbnails


async def add_test_users(session: AsyncSession):
    await add_user(session, "RuteNL", "squirrel", Role.ADMIN)
    await add_user(session, "Ruurd", "squirrel", Role.USER)
    await add_user(session, "Bijlsma", "squirrel", Role.USER)


async def on_startup(app: FastAPI) -> None:
    if not app_config.thumbnails_dir.exists():
        app_config.thumbnails_dir.mkdir(exist_ok=True)

    print("Running migrations")
    await migrate_db(app_config.connection_string)
    print("Migration complete")

    async with get_session() as session:
        await add_test_users(session)
        await process_all(session)

    process = multiprocessing.Process(target=watch_files)
    process.start()

    if app_config.host_thumbnails:
        host_thumbnails(app)

    print("Starting server!")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        await on_startup(app)
    except Exception as e:
        logging.exception("Exception in lifespan:startup!")
        raise e
    yield
    print("Closing server :(")
