import hashlib
import logging
from pathlib import Path

from PIL import Image
from sqlalchemy.orm import Session

from photos.config.app_config import app_config
from photos.config.process_config import process_config
from photos.database.models import ImageModel
from photos.image_modules.base_info import base_info
from photos.image_modules.exif import get_exif
from photos.image_modules.thumbnails import generate_thumbnails
from photos.interfaces import ImageInfo
from photos.utils import clean_object

logger = logging.getLogger(__name__)


def store_image(image_info: ImageInfo, session: Session) -> ImageModel:
    logger.info(image_info)
    cleaned_dict=clean_object(image_info.dict())
    assert isinstance(cleaned_dict, dict)
    image_model = ImageModel(**cleaned_dict)
    session.add(image_model)
    session.commit()
    session.refresh(image_model)
    return image_model


def image_exists(image_path: Path, session: Session) -> bool:
    relative_path = str(image_path.relative_to(app_config.photos_dir))
    image_model = (
        session.query(ImageModel).filter_by(
            relative_path=relative_path
        ).first()
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


def hash_image(image_path: Path, chunk_size: int = 65536) -> str:
    hasher = hashlib.sha256()

    with image_path.open('rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            hasher.update(chunk)

    return hasher.hexdigest()


def process_image(
        photos_dir: Path,
        image_path: Path,
        session: Session
) -> None:
    image_hash = hash_image(image_path)

    if image_exists(image_path, session):
        logger.info(f"Image {image_path} exists, skipping")
        return

    image_info = base_info(photos_dir, image_path, image_hash)
    with Image.open(photos_dir / image_info.relative_path) as img:
        generate_thumbnails(img, image_info)
        image_info = get_exif(img, image_info)

    store_image(image_info, session)
