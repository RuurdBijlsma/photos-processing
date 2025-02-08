from app.routers.job_router_factory import create_job_router
from app.routers.process.process_model import (
    ProcessingJob,
    ProcessingRequest,
    job_db,
    start_job,
)

process_router = create_job_router(
    prefix="/process",
    tags=["process"],
    request_model=ProcessingRequest,
    job_model=ProcessingJob,
    job_db=job_db,
    start_job_func=start_job,
)