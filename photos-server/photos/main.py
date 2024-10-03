import logging
import multiprocessing
import os
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from tqdm import tqdm

from photos.config.app_config import app_config
from photos.config.process_config import process_config
from photos.database.database import get_session_maker
from photos.database.migrations import run_migrations
from photos.ingest.ingest_watch import process_images_in_directory, watch_for_photos
from photos.ingest.process_image import hash_image
from photos.routers import images, health

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Running migrations")
    run_migrations("alembic", app_config.connection_string)
    logger.info("Migration complete")

    process_images_in_directory(app_config.photos_dir)
    process = multiprocessing.Process(target=watch_for_photos, args=(app_config.photos_dir,))
    process.start()

    logger.info("Starting server!")
    yield
    logger.info("Closing server :(")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(images.router)
app.include_router(health.router)

if app_config.host_thumbnails:
    app.mount(
        "/thumbnails",
        StaticFiles(
            directory=process_config.thumbnails_dir,
        ),
        name="Thumbnails",
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=9475,
        log_level="info",
        log_config="logging.yaml",
    )
