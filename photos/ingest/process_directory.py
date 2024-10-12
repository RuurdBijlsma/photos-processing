import itertools
import logging
import os
import shutil
import string
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
from photos.database.models import ImageModel
from photos.ingest.process_image import process_image

logger = logging.getLogger(__name__)
tf = TimezoneFinder()


def fix_image_timezone(
    image: ImageModel, session: Session
) -> None | tuple[float, float]:
    stmt = (
        select(ImageModel)
        .where(ImageModel.latitude.isnot(None))
        .where(ImageModel.longitude.isnot(None))
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


def fill_timezone_gaps() -> None:
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
            closest_image_coordinates.append(fix_image_timezone(image, session))
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
    relative_path = str(image_path.relative_to(app_config.photos_dir))
    image_model = (
        session.query(ImageModel).filter_by(relative_path=relative_path).first()
    )
    if image_model is None:
        return False

    assert image_model.id is not None
    # Check for each resolution
    for size in process_config.thumbnail_sizes:
        file_path = process_config.thumbnails_dir / image_model.id / f"{size}p.webp"
        if not file_path.exists():
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


print_column = 0
console_width = shutil.get_terminal_size().columns


def print_char(char: str) -> None:
    global print_column
    print_column += len(char)
    if print_column >= console_width:
        print_column = 0
        print("", flush=True)
    print(char, end="")


def process_image_list(
    photos_dir: Path, image_list: list[Path], identifier: str
) -> None:
    """Process a chunk of images with a separate session."""
    session = get_session_maker()()
    try:
        print_char("[")

        for image_path in image_list:
            print_char(identifier)
            process_image(photos_dir, image_path, session)
    finally:
        print_char(f"{identifier}]")
        session.close()


def process_images_in_directory(photos_dir: Path) -> None:
    """Check all images for processing."""
    session = get_session_maker()()
    try:
        image_files: list[Path] = []
        for file in tqdm(
            list(photos_dir.rglob("*")), desc="Finding image files", unit="file"
        ):
            if (
                file.suffix.lower() in process_config.image_suffixes
                and not image_exists(file, session)
            ):
                image_files.append(file)
    finally:
        session.close()

    print(f"Found {len(image_files)} images, processing...")
    global print_column
    print_column = 0
    if app_config.multithreaded_processing:
        core_count = os.cpu_count()
        assert core_count is not None
        # If you have more than 94 cores you will be sad
        image_chunks = list(
            zip(
                chunk_list_itertools(image_files, core_count),
                list(string.digits)
                + list(string.ascii_lowercase)
                + list(string.ascii_uppercase)
                + list(string.punctuation),
            )
        )
        with ThreadPoolExecutor(max_workers=core_count) as executor:
            executor.map(
                lambda id_chunk: process_image_list(
                    photos_dir, id_chunk[0], id_chunk[1]
                ),
                image_chunks,
            )
        print("")
    else:
        process_image_list(photos_dir, image_files, ".")

    fill_timezone_gaps()
