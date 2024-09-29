from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from watchdog.observers import Observer

import constants
from basic_photos import process_all, NewImageHandler
from database import get_session, ImageModel, ThumbnailModel
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    process_all()
    event_handler = NewImageHandler(constants.THUMBNAIL_SIZES, constants.THUMBNAILS_DIR)
    print("Watching for new files...")
    observer = Observer()
    observer.schedule(event_handler, constants.PHOTOS_DIR, recursive=True)
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


# Pydantic model for response
class Thumbnail(BaseModel):
    width: int
    height: int
    size: int
    path: str


class ImageResponse(BaseModel):
    id: UUID
    filename: str
    path: str
    format: str
    width: int
    height: int
    thumbnails: list[Thumbnail]


# Endpoint to get images with pagination
@app.get("/images/", response_model=list[ImageResponse])
def get_images(page: int = Query(1, ge=1), limit: int = Query(10, ge=1), session: Session = Depends(get_session)):
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
        response.append({
            "id": image.id,
            "filename": image.filename,
            "path": f"/images/{image.id}",
            "format": image.format,
            "width": image.width,
            "height": image.height,
            "thumbnails": thumbnails
        })
    return response


# Endpoint to serve thumbnail images by ID
@app.get("/thumbnails/{thumbnail_id}")
def get_thumbnail(thumbnail_id: UUID, session: Session = Depends(get_session)):
    # Fetch the thumbnail record from the database
    thumbnail = session.query(ThumbnailModel).filter_by(id=thumbnail_id).first()

    if not thumbnail:
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    # Check if the thumbnail file exists on disk
    if not os.path.exists(thumbnail.path):
        raise HTTPException(status_code=404, detail="Thumbnail file not found")

    # Return the thumbnail file as a response
    return FileResponse(thumbnail.path)


@app.get("/images/{image_id}")
def get_image(image_id: UUID, session: Session = Depends(get_session)):
    # Fetch the image record from the database
    image = session.query(ImageModel).filter_by(id=image_id).first()

    if not image:
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    img_path = os.path.join(constants.PHOTOS_DIR, image.filename)

    # Check if the thumbnail file exists on disk
    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="Thumbnail file not found")

    # Return the thumbnail file as a response
    return FileResponse(img_path, media_type="image/webp")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9475)
