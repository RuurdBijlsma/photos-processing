import os
from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles

from photos.config.app_config import app_config
from photos.database.database import get_session
from photos.database.migrations import run_migrations
from photos.database.models import ImageModel
from photos.interfaces import ImageInfo


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    print("Running migrations")
    run_migrations("alembic", app_config.connection_string)
    print("Migration complete, starting server")
    yield
    print("Closing server")


# Define the FastAPI app
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/images", response_model=ImageInfo)
def post_image(
    image_info: ImageInfo, session: Session = Depends(get_session)
) -> ImageModel:
    print(image_info)
    image_model = ImageModel(**image_info.dict())
    session.add(image_model)
    session.commit()
    session.refresh(image_model)
    return image_model


@app.get("/images", response_model=list[ImageInfo])
def get_images(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session: Session = Depends(get_session),
) -> Sequence[ImageModel]:
    offset = (page - 1) * limit
    images = (
        session.execute(select(ImageModel).offset(offset).limit(limit)).scalars().all()
    )

    if not images:
        raise HTTPException(status_code=404, detail="No images found")

    return images


def get_file_response(
    record: ImageModel,
    photos_dir: Path,
    media_type: str | None = None,
) -> FileResponse:
    if not record:
        raise HTTPException(status_code=404, detail="Not found")

    assert record.filename is not None
    img_path = photos_dir / record.filename

    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(img_path, media_type=media_type)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if app_config.host_thumbnails:
    app.mount(
        "/thumbnails",
        StaticFiles(
            directory=app_config.thumbnails_dir,
        ),
        name="Thumbnails",
    )
