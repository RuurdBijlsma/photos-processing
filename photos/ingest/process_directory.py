import asyncio
import itertools
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TypeVar

import pytz
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from timezonefinder import TimezoneFinder
from tqdm import tqdm

from photos.config.app_config import app_config
from photos.config.process_config import process_config
from photos.database.database import get_session_maker
from photos.database.models import ImageModel, UserModel, GeoLocationModel
from photos.ingest.process_image import process_image
from photos.utils import path_str

logger = logging.getLogger(__name__)
tf = TimezoneFinder()


def fix_image_timezone(
    image: ImageModel, user: UserModel, session: Session
) -> None | tuple[float, float]:
    stmt = (
        select(ImageModel)
        .where(ImageModel.latitude.isnot(None))
        .where(ImageModel.longitude.isnot(None))
        .where(ImageModel.user_id.__eq__(user.id))
        .order_by(
            func.abs(
                func.extract("epoch", ImageModel.datetime_local)
                - func.extract("epoch", image.datetime_local)  # type: ignore
            )
        )
        .limit(1)
    )

    # Execute the query
    result = session.execute(stmt).scalars().first()
    if result is None or not (result.latitude and result.longitude):
        return None
    return float(result.latitude), float(result.longitude)


def fill_timezone_gaps(user: UserModel) -> None:
    session = get_session_maker()()
    try:
        images = (
            session.execute(
                select(ImageModel).where(ImageModel.timezone_name.is_(None))
            )
            .scalars()
            .all()
        )
        closest_image_coordinates: list[tuple[float, float] | None] = []
        for image in tqdm(images, desc="Finding image timezones", unit="image"):
            closest_image_coordinates.append(fix_image_timezone(image, user, session))
        for image, coordinate in tqdm(
            list(zip(images, closest_image_coordinates)),
            desc="Fixing timezones",
            unit="image",
        ):
            if coordinate is None:
                continue
            latitude, longitude = coordinate
            timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
            if timezone_str is None:
                continue
            local_tz = pytz.timezone(timezone_str)
            assert image.datetime_local is not None
            local_dt = local_tz.localize(image.datetime_local)
            assert local_dt is not None
            image.datetime_utc = local_dt.astimezone(pytz.utc)
            image.timezone_name = timezone_str
            image.timezone_offset = local_dt.utcoffset()
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"An exception occurred: {e}")
    finally:
        session.close()


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


T = TypeVar("T")


def chunk_list_itertools(data: list[T], n: int) -> list[list[T]]:
    """Split a list into n chunks using itertools."""
    it = iter(data)
    return [
        list(itertools.islice(it, i))
        for i in [len(data) // n + (1 if x < len(data) % n else 0) for x in range(n)]
    ]


async def process_image_list(image_list: list[Path], user: UserModel) -> None:
    """Process a chunk of images with a separate session."""
    session = get_session_maker()()
    try:
        for image_path in image_list:
            await process_image(image_path, user, session)
    finally:
        session.close()


def remove_dangling_entries(session: Session, image_files: list[Path]) -> None:
    db_images = session.query(ImageModel).all()
    relative_paths = [path_str(path) for path in image_files]
    for image_model in db_images:
        if image_model.relative_path not in relative_paths:
            session.delete(image_model)
            print(
                f"Deleting {image_model.relative_path}, the file does not exist anymore."
            )
    session.commit()

    locations_without_images = (
        session.query(GeoLocationModel)
        .outerjoin(ImageModel, GeoLocationModel.id == ImageModel.location_id)
        .filter(ImageModel.id.is_(None))
        .all()
    )
    for location in locations_without_images:
        print(f"Deleting {location}, the location has no images anymore.")
        session.delete(location)
    session.commit()


async def process_images_in_directory(directory: Path, user: UserModel) -> None:
    """Check all images for processing."""
    session = get_session_maker()()
    image_files = [
        file
        for file in directory.rglob("*")
        if file.suffix.lower() in process_config.media_suffixes
    ]
    remove_dangling_entries(session, image_files)

    try:
        images_to_process: list[Path] = []
        for file in tqdm(image_files, desc="Finding image files", unit="file"):
            if not image_exists(file, session):
                images_to_process.append(file)
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
