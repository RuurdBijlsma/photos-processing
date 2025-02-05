import uuid

from fastapi import APIRouter, HTTPException, BackgroundTasks
from media_analyzer import MediaAnalyzer
from media_analyzer.data.interfaces.api_io import MediaAnalyzerOutput, InputMedia
from pydantic import BaseModel

from app.config import app_config
from app.processing.generate_thumbnails import generate_thumbnails
from app.processing.process_utils import has_all_thumbnails, hash_image, get_thumbnail_paths

process_router = APIRouter(prefix="/process", tags=["process"])


class ProcessingJob(BaseModel):
    job_id: str
    result: MediaAnalyzerOutput | None = None
    done: bool = False


class ProcessingRequest(BaseModel):
    relative_path: str


job_db: dict[str, ProcessingJob] = {}
analyzer = MediaAnalyzer()


async def start_job(job_id: str, image: ProcessingRequest) -> None:
    job_db[job_id] = ProcessingJob(job_id=job_id)
    image_path = app_config.images_dir / image.relative_path
    image_hash = hash_image(image_path)
    print(f"STARTING {image_path} {image_hash}")
    thumbnail_paths = get_thumbnail_paths(image_path, image_hash)
    if not has_all_thumbnails(thumbnail_paths):
        await generate_thumbnails(image_path, image_hash)
    print(f"THUMBNAILS ARE DONE")
    job_db[job_id].result = analyzer.analyze(InputMedia(
        path=image_path,
        frames=list(thumbnail_paths.frames.values()),
    ))
    print(f"ALL DONE {job_id}")
    job_db[job_id].done = True


@process_router.post("")
async def start_processing_image(
    image: ProcessingRequest,
    background_tasks: BackgroundTasks
) -> str:
    job_id = uuid.uuid4().hex
    background_tasks.add_task(start_job, job_id, image)
    return job_id


@process_router.get("/{job_id}")
async def get_job_status(job_id: str) -> ProcessingJob:
    if job_id not in job_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_db[job_id]


@process_router.delete("/{job_id}")
async def delete_job_status(job_id: str) -> bool:
    if job_id not in job_db:
        raise HTTPException(status_code=404, detail="Job not found")
    del job_db[job_id]
    return True


@process_router.get("/")
async def list_job_statuses() -> list[ProcessingJob]:
    return list(job_db.values())
