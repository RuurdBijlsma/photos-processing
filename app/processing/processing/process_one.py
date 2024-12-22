from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.data.database.image_operations import store_image
from app.processing.pipeline.pipeline import run_metadata_pipeline
from app.processing.processing.generate_thumbnails import generate_generic_thumbnails
from app.processing.processing.process_utils import get_thumbnail_paths, hash_image


async def process_one(image_path: Path, user_id: int, session: AsyncSession) -> None:
    image_hash = hash_image(image_path)
    await generate_generic_thumbnails(image_path, image_hash)
    image_info, frames = run_metadata_pipeline(
        image_path,
        image_hash,
        get_thumbnail_paths(image_path, image_hash),
    )
    await store_image(image_info, frames, user_id, session)
