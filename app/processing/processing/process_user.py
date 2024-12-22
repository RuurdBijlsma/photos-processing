from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession
from tqdm import tqdm

from app.config.app_config import app_config
from app.data.database.image_operations import store_image
from app.processing.cleanup.cleanup_entries import cleanup_entries
from app.processing.cleanup.drop_images_without_thumbnails import (
    drop_images_without_thumbnails,
)
from app.processing.pipeline.pipeline import run_metadata_pipeline
from app.processing.post_processing.fix_timezone import fill_timezone_gaps
from app.processing.processing.generate_thumbnails import (
    generate_photo_thumbnails,
    generate_video_thumbnails,
)
from app.processing.processing.process_utils import (
    get_thumbnail_paths,
    hash_image,
    image_needs_processing,
)

if TYPE_CHECKING:
    from pathlib import Path


async def process_user_images(
    user_id: int,
    username: str,
    session: AsyncSession,
) -> None:
    """Check all images for processing."""
    directory = app_config.images_dir / str(user_id)
    print(f"Processing images for user {username}")
    image_files = [
        file
        for file in directory.rglob("*")
        if file.suffix.lower() in app_config.image_suffixes
    ]
    # Remove db images where the file is gone:
    await cleanup_entries(session, user_id, image_files)

    photos_to_process: list[Path] = []
    videos_to_process: list[Path] = []
    for file in image_files:
        if await image_needs_processing(file, session):
            if file.suffix in app_config.photo_suffixes:
                photos_to_process.append(file)
            if file.suffix in app_config.video_suffixes:
                videos_to_process.append(file)

    await drop_images_without_thumbnails(photos_to_process + videos_to_process, session)

    failed_photos = generate_photo_thumbnails(photos_to_process)
    failed_videos = await generate_video_thumbnails(videos_to_process)

    to_process_zip = (
        list(zip(photos_to_process, failed_photos, strict=False)) +
        list(zip(videos_to_process, failed_videos, strict=False))
    )

    for image_path, has_thumbnails in tqdm(
        to_process_zip,
        desc="Gathering image metadata.",
        unit="file",
    ):
        if not has_thumbnails:
            print(f"Skipping {image_path}, the thumbnail for it failed.")
            continue
        image_hash = hash_image(image_path)
        image_info, frames = run_metadata_pipeline(
            image_path,
            image_hash,
            get_thumbnail_paths(image_path, image_hash),
        )
        await store_image(image_info, frames, user_id, session)

    await fill_timezone_gaps(session, user_id)
