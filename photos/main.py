import logging
import multiprocessing
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from photos.config.app_config import app_config
from photos.config.process_config import process_config
from photos.database.migrations import run_migrations
from photos.ingest.process_directory import process_images_in_directory
from photos.ingest.watch_directory import watch_for_photos
from photos.routers import images, health, auth

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Running migrations")
    run_migrations("alembic", app_config.connection_string)
    logger.info("Migration complete")

    process_images_in_directory(app_config.photos_dir)
    process = multiprocessing.Process(
        target=watch_for_photos, args=(app_config.photos_dir,)
    )
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
app.include_router(auth.router)

if not process_config.thumbnails_dir.exists():
    process_config.thumbnails_dir.mkdir(exist_ok=True)
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
