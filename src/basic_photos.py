import hashlib
import os
from typing import Any

from PIL import Image
from sqlalchemy import exists
from tqdm import tqdm
from watchdog.events import FileSystemEventHandler

import constants
from database import get_session_maker, ImageModel, ThumbnailModel


# Function to generate thumbnail and save it in WEBP format
def pillow_process(image_path, thumbnail_sizes, output_dir) -> dict[str, Any]:
    # Open the original image
    with Image.open(image_path) as img:
        original_width, original_height = img.size
        original_format = img.format
        image_info = {
            "filename": os.path.basename(image_path),
            "format": original_format,
            "width": original_width,
            "height": original_height,
            "thumbnails": [],
        }

        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate thumbnails
        for size in thumbnail_sizes:
            img_copy = img.copy()
            img_copy.thumbnail((size, size))
            thumb_name = f"thumb_{os.path.basename(image_path)}_{size}.webp"
            thumb_path = os.path.join(output_dir, thumb_name)
            img_copy.save(thumb_path, format="WEBP")

            # Collect thumbnail info
            image_info["thumbnails"].append(
                {
                    "width": img_copy.width,
                    "height": img_copy.height,
                    "size": size,
                    "filename": thumb_name,
                }
            )

    return image_info


# Function to insert image metadata into the database using SQLAlchemy
def insert_image_metadata(session, image_info) -> None:
    try:
        # Insert the image record
        image_record = ImageModel(
            filename=image_info["filename"],
            format=image_info["format"],
            width=image_info["width"],
            height=image_info["height"],
            hash=image_info["hash"],
        )
        session.add(image_record)
        session.flush()  # Ensure image record is written to get its id

        # Insert each thumbnail record
        for thumbnail in image_info["thumbnails"]:
            thumbnail_record = ThumbnailModel(
                image_id=image_record.id,
                size=thumbnail["size"],
                width=thumbnail["width"],
                height=thumbnail["height"],
                filename=thumbnail["filename"],
            )
            session.add(thumbnail_record)

        # Commit all changes
        session.commit()

    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")


# Function to check if an image already exists in the database by filename
def image_exists_in_db(session, filename) -> bool:
    return session.query(exists().where(ImageModel.filename == filename)).scalar()


def image_exists_by_hash(session, image_hash) -> str:
    return session.query(exists().where(ImageModel.hash == image_hash)).scalar()


# Function to hash image content for a unique identifier (optional, but more robust)
def hash_image(image_path) -> str:
    hash_md5 = hashlib.md5()
    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# Main function to process the image
def process_image(image_path, thumbnail_sizes, output_dir, session) -> None:
    # Compute the hash of the image
    image_hash = hash_image(image_path)

    # Check if an image with this hash already exists in the database
    if image_exists_by_hash(session, image_hash) and image_exists_in_db(
        session, os.path.basename(image_path)
    ):
        # print(f"Image '{image_path}' with hash '{image_hash}' already exists in the database. Skipping...")
        session.close()
        return

    # If the image does not exist, proceed with processing
    image_info = pillow_process(image_path, thumbnail_sizes, output_dir)

    # Insert the hash along with the image metadata
    image_info["hash"] = image_hash
    insert_image_metadata(session, image_info)

    # Close the session
    session.close()
    # print(f"Processed and added image '{image_path}' to the database.")


# Function to process all images in a directory (recursively)
def process_images_in_directory(directory_path, thumbnail_sizes, output_dir) -> None:
    image_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(
                (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp")
            ):
                image_files.append(os.path.join(root, file))

    session = get_session_maker()()
    # Use tqdm to show progress
    for image_path in tqdm(image_files, desc="Processing images", unit="image"):
        process_image(image_path, thumbnail_sizes, output_dir, session)


# Watchdog event handler for new files
class NewImageHandler(FileSystemEventHandler):
    def __init__(self, thumbnail_sizes, output_dir):
        self.thumbnail_sizes = thumbnail_sizes
        self.output_dir = output_dir

    def on_created(self, event) -> None:
        session = get_session_maker()()
        try:
            # If a new file is created and is an image, process it
            if not event.is_directory and event.src_path.lower().endswith(
                (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp")
            ):
                print("Processing new photo")
                process_image(
                    event.src_path, self.thumbnail_sizes, self.output_dir, session
                )
        finally:
            session.close()


def process_all() -> None:
    # Process all existing images in the directory
    process_images_in_directory(
        constants.PHOTOS_DIR, constants.THUMBNAIL_SIZES, constants.THUMBNAILS_DIR
    )

    print("Watching for new photos.")


# Example usage
if __name__ == "__main__":
    process_all()
