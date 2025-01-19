import shutil

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_config import app_config
from app.data.image_models import ImageModel


async def cleanup_thumbnails(session: AsyncSession) -> None:
    """Remove thumbnails for images that don't exist."""
    thumbnails = {folder.name for folder in app_config.thumbnails_dir.iterdir()}
    db_hashes = {img_hash for (img_hash,) in (await session.execute(select(ImageModel.hash))).all()}
    for dangling_thumbnail in thumbnails - db_hashes:
        print(f"Thumbnail {dangling_thumbnail} has no images, deleting.")
        shutil.rmtree(app_config.thumbnails_dir / dangling_thumbnail)
