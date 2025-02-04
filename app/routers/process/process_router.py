import uuid

from fastapi import APIRouter, HTTPException
from media_analyzer.data.interfaces.api_io import MediaAnalyzerOutput
from pydantic import BaseModel

process_router = APIRouter(prefix="/process", tags=["process"])


class ProcessingJob(BaseModel):
    job_id: str
    result: MediaAnalyzerOutput | None = None
    done: bool = False


class ProcessingRequest(BaseModel):
    relative_path: str


job_db: dict[str, ProcessingJob]


@process_router.post("")
async def start_processing_image(image: ProcessingRequest) -> str:
    job_id = uuid.uuid4().hex
    job_db[job_id] = ProcessingJob(job_id=job_id)
    # todo: process image, generate thumbnail if not available yet
    return job_id


@process_router.post("/status/{job_id}")
async def get_job_status(job_id: str) -> ProcessingJob:
    if job_id not in job_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_db[job_id]
