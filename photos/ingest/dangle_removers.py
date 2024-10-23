import shutil
from pathlib import Path

from sqlalchemy.orm import Session

from photos.config.process_config import process_config
from photos.database.database import get_session_maker
from photos.database.models import ImageModel, GeoLocationModel
from photos.utils import path_str


def remove_dangling_entries(
    session: Session, user_id: int, image_files: list[Path]
) -> None:
    db_images = session.query(ImageModel).filter_by(user_id=user_id).all()
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


def remove_dangling_thumbnails() -> None:
    """Remove thumbnails for images that don't exist."""
    session = get_session_maker()()
    thumbnails = {folder.name for folder in process_config.thumbnails_dir.iterdir()}
    db_hashes = {img_hash for (img_hash,) in session.query(ImageModel.hash).all()}
    for dangling_thumbnail in thumbnails - db_hashes:
        print(f"Thumbnail {dangling_thumbnail} has no images, deleting.")
        shutil.rmtree(process_config.thumbnails_dir / dangling_thumbnail)


def remove_images_with_no_thumbnails(images_to_process: list[Path], session: Session) -> None:
    for image in images_to_process:
        # image is to be processed, but may already be in db (has no thumbnails)
        # Remove from db in this case
        image_model = session.query(ImageModel).filter_by(relative_path=path_str(image)).first()
        if image_model is None:
            continue
        print(f"Deleting {image_model.relative_path}, it has no thumbnails.")
        session.delete(image_model)
    session.commit()
