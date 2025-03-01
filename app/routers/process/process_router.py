import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.routers.process.process_model import ProcessingJob, ProcessingRequest, job_db, start_job

process_router = APIRouter(prefix="/process", tags=["process"])


@process_router.post("")
async def start_processing(data: ProcessingRequest, background_tasks: BackgroundTasks) -> str:
    job_id = uuid.uuid4().hex
    background_tasks.add_task(start_job, job_id, data)
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


@process_router.get("")
async def list_job_statuses() -> list[ProcessingJob]:
    return list(job_db.values())
