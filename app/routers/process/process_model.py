import asyncio

from media_analyzer import MediaAnalyzer
from media_analyzer.data.interfaces.api_io import InputMedia, MediaAnalyzerOutput
from pydantic import BaseModel

from app.config import app_config
from app.processing.generate_thumbnails import generate_thumbnails
from app.processing.process_utils import get_thumbnail_paths, has_all_thumbnails, hash_image


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
        await asyncio.to_thread(generate_thumbnails, image_path, image_hash)
    print("THUMBNAILS ARE DONE")
    media = InputMedia(
        path=image_path,
        frames=list(thumbnail_paths.frames.values()),
    )
    job_db[job_id].result = await asyncio.to_thread(analyzer.analyze, media)
    print(f"ALL DONE {job_id}")
    job_db[job_id].done = True
