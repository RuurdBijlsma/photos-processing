import logging
import multiprocessing
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_config import app_config
from app.data.database.database import get_session
from app.data.database.db_utils import add_user
from app.data.database.migrations import migrate_db
from app.data.enums.user_role import Role
from app.processing.processing.process_all import process_all
from app.processing.watch.watch_for_changes import watch_files
from app.server.host_thumbnails import host_thumbnails


async def add_test_users(session: AsyncSession) -> None:
    await add_user(session, "RuteNL", "squirrel", Role.ADMIN)
    await add_user(session, "Ruurd", "squirrel", Role.USER)
    await add_user(session, "Bijlsma", "squirrel", Role.USER)



async def on_startup(app: FastAPI) -> None:
    if not app_config.disable_processing:
        if not app_config.thumbnails_dir.exists():
            app_config.thumbnails_dir.mkdir(exist_ok=True, parents=True)
        if not app_config.images_dir.exists():
            app_config.images_dir.mkdir(exist_ok=True, parents=True)

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
    except Exception:
        logging.exception("Exception in lifespan:startup!")
        raise
    yield
    print("Closing server :(")
