from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.database.db_utils import path_str
from app.data.image_models import GeoLocationModel, ImageModel


async def cleanup_entries(
    session: AsyncSession, user_id: int, image_files: list[Path],
) -> None:
    """Delete images from db that don't have a corresponding image file.
    Also delete geolocation entries that no longer have any associated images.

    Args:
        session: AsyncSession object.
        user_id: ID of the user whose images are being cleaned up.
        image_files: List of Path objects representing image files.

    """
    db_images = (
        (await session.execute(select(ImageModel).filter_by(user_id=user_id)))
        .scalars()
        .all()
    )

    relative_paths = [path_str(path) for path in image_files]
    for image_model in db_images:
        if image_model.relative_path not in relative_paths:
            await session.delete(image_model)
            print(
                f"Deleting {image_model.relative_path}, "
                "the file does not exist anymore.",
            )

    locations_without_images = (
        await session.execute(
            select(GeoLocationModel)
            .outerjoin(ImageModel, GeoLocationModel.id == ImageModel.location_id)
            .filter(ImageModel.id.is_(None)),
        )
    ).scalars().all()

    for location in locations_without_images:
        print(f"Deleting {location}, the location has no images anymore.")
        await session.delete(location)
    await session.commit()
