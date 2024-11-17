from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.config.app_config import app_config


def host_thumbnails(app: FastAPI) -> None:
    app.mount(
        "/thumbnails",
        StaticFiles(
            directory=app_config.thumbnails_dir,
        ),
        name="Thumbnails",
    )
