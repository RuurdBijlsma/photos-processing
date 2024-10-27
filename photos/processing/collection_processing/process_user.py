from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tqdm import tqdm

from photos.config.app_config import app_config
from photos.data.database.db_utils import path_str
from photos.data.models.image_models import ImageModel
from photos.processing.cleanup.cleanup_entries import cleanup_entries
from photos.processing.cleanup.drop_images_without_thumbnails import drop_images_without_thumbnails
from photos.processing.post_processing.fix_timezone import fill_timezone_gaps
from photos.processing.process_image import process_media


async def image_exists(image_path: Path, session: AsyncSession) -> bool:
    image_model = (await session.execute(
        select(ImageModel).filter_by(relative_path=path_str(image_path))
    )).scalar_one_or_none()
    if image_model is None:
        return False

    assert image_model.hash is not None
    # Check for each resolution
    for size in app_config.thumbnail_heights:
        file_path = app_config.thumbnails_dir / image_model.hash / f"{size}p.avif"
        if not file_path.exists():
            return False

    if image_path.suffix in app_config.video_suffixes:
        vid_path = app_config.thumbnails_dir / image_model.hash / "vid.webm"
        if not vid_path.exists():
            return False

    return True


async def process_image_list(session: AsyncSession, image_list: list[Path], user_id: int) -> None:
    """Process a chunk of images with a separate db session."""
    for image_path in image_list:
        await process_media(image_path, user_id, session)


async def process_user_images(user_id: int, username: str, session: AsyncSession) -> None:
    """Check all images for processing."""
    directory = app_config.images_dir / str(user_id)
    print(f"Processing images for user {username}")
    image_files = [
        file
        for file in directory.rglob("*")
        if file.suffix.lower() in app_config.image_suffixes
    ]
    await cleanup_entries(session, user_id, image_files)

    images_to_process: list[Path] = []
    for file in tqdm(image_files, desc="Finding image files", unit="file"):
        if not await image_exists(file, session):
            images_to_process.append(file)
    await drop_images_without_thumbnails(images_to_process, session)

    print(f"Found {len(images_to_process)} images, processing...")
    await process_image_list(session, images_to_process, user_id)

    await fill_timezone_gaps(session, user_id)
