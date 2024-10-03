import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from photos.config.app_config import app_config
from photos.database.migrations import run_migrations
from photos.routers import images, health

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Running migrations")
    run_migrations("alembic", app_config.connection_string)
    logger.info("Migration complete, starting server")
    yield
    logger.info("Closing server")


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
            directory=app_config.thumbnails_dir,
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
