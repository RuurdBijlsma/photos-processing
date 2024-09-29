import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from watchdog.observers import Observer

from photos import constants
from photos.basic_photos import process_all, NewImageHandler
from photos.database import get_session, ImageModel, ThumbnailModel, run_migrations
from photos.interfaces import ImageResponse


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    run_migrations("alembic", constants.CONNECTION_STRING)
    process_all()
    event_handler = NewImageHandler(constants.THUMBNAIL_SIZES, constants.THUMBNAILS_DIR)
    print("Watching for new files...")
    observer = Observer()
    observer.schedule(event_handler, str(constants.PHOTOS_DIR), recursive=True)
    observer.start()
    print("Starting server")
    yield
    print("Closing server")
    observer.stop()
    observer.join()


# Define the FastAPI app
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Endpoint to get images with pagination
@app.get("/images/", response_model=list[ImageResponse])
def get_images(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session: Session = Depends(get_session),
) -> list[dict[str, Any]]:
    # Calculate offset for pagination
    offset = (page - 1) * limit

    # Query the database to get the images and their thumbnails
    images = session.query(ImageModel).offset(offset).limit(limit).all()

    if not images:
        raise HTTPException(status_code=404, detail="No images found")

    # Prepare the response data
    response = []
    for image in images:
        thumbnails = [
            {
                "width": thumbnail.width,
                "height": thumbnail.height,
                "size": thumbnail.size,
                "path": f"/thumbnails/{thumbnail.id}",
            }
            for thumbnail in image.thumbnails
        ]
        response.append(
            {
                "id": image.id,
                "filename": image.filename,
                "path": f"/images/{image.id}",
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "thumbnails": thumbnails,
            }
        )
    return response


def get_file_response(
    record: ThumbnailModel | ImageModel | None,
    base_dir: Path,
    media_type: str | None = None,
) -> FileResponse:
    if not record:
        raise HTTPException(status_code=404, detail="Not found")

    img_path = base_dir / record.filename

    # Check if the thumbnail file exists on disk
    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Return the thumbnail file as a response
    return FileResponse(img_path, media_type=media_type)


# Endpoint to serve thumbnail images by ID
@app.get("/thumbnails/{thumbnail_id}")
def get_thumbnail(
    thumbnail_id: UUID, session: Session = Depends(get_session)
) -> FileResponse:
    # Fetch the thumbnail record from the database
    thumbnail = session.query(ThumbnailModel).filter_by(id=thumbnail_id).first()
    return get_file_response(thumbnail, constants.THUMBNAILS_DIR)


@app.get("/images/{image_id}")
def get_image(image_id: UUID, session: Session = Depends(get_session)) -> FileResponse:
    # Fetch the image record from the database
    image = session.query(ImageModel).filter_by(id=image_id).first()
    return get_file_response(image, constants.PHOTOS_DIR, "image/webp")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9475)
