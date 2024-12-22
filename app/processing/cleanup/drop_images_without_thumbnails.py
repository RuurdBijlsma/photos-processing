from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.database.db_utils import path_str
from app.data.image_models import ImageModel


async def drop_images_without_thumbnails(
    images_to_process: list[Path], session: AsyncSession,
) -> None:
    for image in images_to_process:
        # image is to be processed, but may already be in db (has no thumbnails)
        # Remove from db in this case
        image_model = (
            await session.execute(
                select(ImageModel).filter_by(relative_path=path_str(image)),
            )
        ).scalar_one_or_none()
        if image_model is None:
            continue
        print(f"Deleting {image_model.relative_path}, it has no thumbnails.")
        await session.delete(image_model)
    await session.commit()
