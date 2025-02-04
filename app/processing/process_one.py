from pathlib import Path

from media_analyzer import InputMedia
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.database.image_operations import store_image
from app.processing.generate_thumbnails import generate_thumbnails
from app.processing.process_utils import analyzer, get_thumbnail_paths, hash_image


async def process_image(
    image_path: Path,
    image_hash: str,
    user_id: int,
    session: AsyncSession,
) -> None:
    thumb_paths = get_thumbnail_paths(image_path, image_hash)
    result = analyzer.analyze(
        InputMedia(
            path=image_path,
            frames=list(thumb_paths.frames.values()),
        ),
    )

    await store_image(result, user_id, session)


async def process_one(image_path: Path, user_id: int, session: AsyncSession) -> None:
    image_hash = hash_image(image_path)
    await generate_thumbnails(image_path, image_hash)
    await process_image(image_path, image_hash, user_id, session)
