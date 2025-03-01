import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.routers.thumbnails.thumbnail_model import ThumbnailJob, ThumbnailRequest, job_db, start_job

thumbnail_router = APIRouter(prefix="/thumbnails", tags=["thumbnails"])


@thumbnail_router.post("")
async def start_processing(data: ThumbnailRequest, background_tasks: BackgroundTasks) -> str:
    job_id = uuid.uuid4().hex
    background_tasks.add_task(start_job, job_id, data)
    return job_id


@thumbnail_router.get("/{job_id}")
async def get_job_status(job_id: str) -> ThumbnailJob:
    if job_id not in job_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_db[job_id]


@thumbnail_router.delete("/{job_id}")
async def delete_job_status(job_id: str) -> bool:
    if job_id not in job_db:
        raise HTTPException(status_code=404, detail="Job not found")
    del job_db[job_id]
    return True


@thumbnail_router.get("")
async def list_job_statuses() -> list[ThumbnailJob]:
    return list(job_db.values())
