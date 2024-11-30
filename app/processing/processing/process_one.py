from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.data.database.image_operations import store_image
from app.processing.processing.generate_thumbnails import generate_generic_thumbnails
from app.processing.pipelines.scan_image import scan_image
from app.processing.processing.process_utils import hash_image, get_thumbnail_paths


async def process_one(image_path: Path, user_id: int, session: AsyncSession) -> None:
    image_hash = hash_image(image_path)
    await generate_generic_thumbnails(image_path, image_hash)
    image_info, frames = scan_image(
        image_path,
        image_hash,
        get_thumbnail_paths(image_path, image_hash)
    )
    await store_image(image_info, frames, user_id, session)
