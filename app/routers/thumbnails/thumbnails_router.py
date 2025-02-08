from app.routers.job_router_factory import create_job_router
from app.routers.thumbnails.thumbnails_model import (
    ThumbnailJob,
    ThumbnailRequest,
    job_db,
    start_job,
)

thumbnails_router = create_job_router(
    prefix="/thumbnails",
    tags=["thumbnails"],
    request_model=ThumbnailRequest,
    job_model=ThumbnailJob,
    job_db=job_db,
    start_job_func=start_job,
)