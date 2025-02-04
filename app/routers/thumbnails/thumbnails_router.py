import uuid

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.config.app_config import app_config
from app.processing.generate_thumbnails import generate_photo_thumbnails, generate_video_thumbnails

thumbnails_router = APIRouter(prefix="/thumbnails", tags=["thumbnails"])


class ThumbnailJob(BaseModel):
    job_id: str
    photos_done: int = 0
    photos_total: int
    photos: list[bool] | None = None
    videos_done: int = 0
    videos_total: int
    videos: list[bool] | None = None
    done: bool = False


class ThumbnailRequest(BaseModel):
    photos: list[str] = Field(description="List of paths to photos, relative to media dir.")
    videos: list[str] = Field(description="List of paths to videos, relative to media dir.")


job_db: dict[str, ThumbnailJob] = {}


async def start_job(job_id: str, thumbnails: ThumbnailRequest) -> None:
    job_db[job_id] = ThumbnailJob(
        job_id=job_id,
        videos_total=len(thumbnails.videos),
        photos_total=len(thumbnails.photos),
    )

    def on_photo_process(done: int) -> None:
        job_db[job_id].photos_done = done

    def on_video_process(done: int) -> None:
        job_db[job_id].videos_done = done

    job_db[job_id].photos = generate_photo_thumbnails([
        app_config.images_dir / relative_path
        for relative_path in thumbnails.photos
    ], on_process=on_photo_process)

    job_db[job_id].videos = await generate_video_thumbnails([
        app_config.images_dir / relative_path
        for relative_path in thumbnails.videos
    ], on_process=on_video_process)

    job_db[job_id].done = True


@thumbnails_router.post("/")
async def start_generate_thumbnails(
    thumbnails: ThumbnailRequest,
    background_tasks: BackgroundTasks,
) -> str:
    job_id = uuid.uuid4().hex
    background_tasks.add_task(start_job, job_id, thumbnails)
    return job_id


@thumbnails_router.get("/status/{job_id}")
async def get_job_status(job_id: str) -> ThumbnailJob:
    if job_id not in job_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_db[job_id]
