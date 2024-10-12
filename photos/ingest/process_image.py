import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from sqlalchemy.orm import Session

from photos.database.models import ImageModel, GeoLocationModel
from photos.image_modules.base_info import base_info
from photos.image_modules.exif import get_exif
from photos.image_modules.gps import get_gps_image
from photos.image_modules.thumbnails import generate_thumbnails
from photos.image_modules.time_taken import get_time_taken
from photos.interfaces import TimeImageInfo
from photos.utils import clean_object

logger = logging.getLogger(__name__)


def store_image(image_info: TimeImageInfo, session: Session) -> ImageModel:
    cleaned_dict = clean_object(image_info.model_dump())
    assert isinstance(cleaned_dict, dict)
    location = cleaned_dict.pop("location")
    location_model = None
    if location and image_info.location:
        location_model = (
            session.query(GeoLocationModel)
            .filter_by(
                city=image_info.location.city,
                province=image_info.location.province,
                country=image_info.location.country,
            )
            .scalar()
        )
        if not location_model:
            location_model = GeoLocationModel(**location)
    image_model = ImageModel(**cleaned_dict, location=location_model)
    session.add(image_model)
    session.commit()
    session.refresh(image_model)
    return image_model


def process_image(photos_dir: Path, image_path: Path, session: Session) -> None:

    image_info = base_info(photos_dir, image_path)

    with ThreadPoolExecutor() as executor:
        thumbnail_future = executor.submit(lambda: generate_thumbnails(image_info))

        image_info = get_exif(image_info)
        image_info = get_gps_image(image_info)
        image_info = get_time_taken(image_info)
        thumbnail_future.result()

        store_image(image_info, session)
