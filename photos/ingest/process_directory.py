import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from sqlalchemy.orm import Session
from tqdm import tqdm

from photos.config.app_config import app_config
from photos.config.process_config import process_config
from photos.database.database import get_session_maker
from photos.database.models import ImageModel, UserModel
from photos.ingest.dangle_removers import remove_dangling_entries, remove_images_with_no_thumbnails, \
    remove_dangling_thumbnails
from photos.ingest.fix_timezone import fill_timezone_gaps
from photos.ingest.process_directory_utils import chunk_list_itertools
from photos.ingest.process_image import process_image
from photos.utils import path_str

logger = logging.getLogger(__name__)


def image_exists(image_path: Path, session: Session) -> bool:
    image_model = (
        session.query(ImageModel).filter_by(relative_path=path_str(image_path)).first()
    )
    if image_model is None:
        return False

    assert image_model.hash is not None
    # Check for each resolution
    for size in process_config.thumbnail_sizes:
        file_path = process_config.thumbnails_dir / image_model.hash / f"{size}p.avif"
        if not file_path.exists():
            return False

    if image_path.suffix in process_config.video_suffixes:
        vid_path = process_config.thumbnails_dir / image_model.hash / "vid.webm"
        if not vid_path.exists():
            return False

    return True


async def process_image_list(image_list: list[Path], user: UserModel) -> None:
    """Process a chunk of images with a separate db session."""
    session = get_session_maker()()
    try:
        for image_path in image_list:
            await process_image(image_path, user, session)
    finally:
        session.close()


async def process_images_in_directory(directory: Path, user: UserModel) -> None:
    print(f"Processing images for user {user.username}")
    """Check all images for processing."""
    session = get_session_maker()()
    image_files = [
        file
        for file in directory.rglob("*")
        if file.suffix.lower() in process_config.media_suffixes
    ]
    assert user.id is not None
    remove_dangling_entries(session, user.id, image_files)

    try:
        images_to_process: list[Path] = []
        for file in tqdm(image_files, desc="Finding image files", unit="file"):
            if not image_exists(file, session):
                images_to_process.append(file)
        remove_images_with_no_thumbnails(images_to_process, session)
    finally:
        session.close()

    print(f"Found {len(images_to_process)} images, processing...")
    if app_config.multithreaded_processing:
        core_count = os.cpu_count()
        assert core_count is not None
        image_chunks = chunk_list_itertools(images_to_process, core_count)
        with ThreadPoolExecutor(max_workers=core_count) as executor:
            executor.map(
                lambda chunk: asyncio.run(process_image_list(chunk, user)),
                image_chunks,
            )
        print("")
    else:
        await process_image_list(images_to_process, user)

    fill_timezone_gaps(user)


async def process_all_user_photos() -> None:
    session = get_session_maker()()
    users = session.query(UserModel).all()
    for user in users:
        assert isinstance(user, UserModel)
        await process_images_in_directory(app_config.photos_dir / str(user.id), user)
    remove_dangling_thumbnails()
