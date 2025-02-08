# app/routers/job_router_factory.py
import uuid
from typing import Type, Callable, Dict

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

def create_job_router(
    prefix: str,
    tags: list[str],
    request_model: Type[BaseModel],
    job_model: Type[BaseModel],
    job_db: Dict[str, BaseModel],
    start_job_func: Callable,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)

    @router.post("", response_model=str)
    async def start_processing(
        data: request_model, background_tasks: BackgroundTasks
    ) -> str:
        job_id = uuid.uuid4().hex
        background_tasks.add_task(start_job_func, job_id, data)
        return job_id

    @router.get("/{job_id}", response_model=job_model)
    async def get_job_status(job_id: str) -> BaseModel:
        if job_id not in job_db:
            raise HTTPException(status_code=404, detail="Job not found")
        return job_db[job_id]

    @router.delete("/{job_id}", response_model=bool)
    async def delete_job_status(job_id: str) -> bool:
        if job_id not in job_db:
            raise HTTPException(status_code=404, detail="Job not found")
        del job_db[job_id]
        return True

    @router.get("/", response_model=list[job_model])
    async def list_job_statuses() -> list[BaseModel]:
        return list(job_db.values())

    return router