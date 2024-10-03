import logging
import os
import sys
import time
from pathlib import Path

from tqdm import tqdm
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, DirCreatedEvent
from watchdog.observers import Observer

from photos.config.app_config import app_config
from photos.config.process_config import process_config
from photos.database.database import get_session_maker
from photos.ingest.process_image import process_image

# Need to set up logging because watchdog in different thread is weird
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
logger.addHandler(handler)


def process_images_in_directory(photos_dir: Path) -> None:
    """Check all images for processing."""
    image_files: list[Path] = []
    for root, _, files in os.walk(photos_dir):
        for file in files:
            if file.lower().endswith(process_config.image_suffixes):
                image_files.append(Path(root) / file)

    session = get_session_maker()()
    logger.info(f"Photos dir: {photos_dir}")
    for image_path in tqdm(image_files, desc="Processing images", unit="image"):
        process_image(photos_dir, image_path, session)


class NewImageHandler(FileSystemEventHandler):
    def __init__(self):
        self.session = get_session_maker()()

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent) -> None:
        source_path = Path(str(event.src_path))
        if (
                not event.is_directory
                and source_path.suffix in process_config.image_suffixes
        ):
            logger.info("[watchdog] Processing new photo!")
            process_image(app_config.photos_dir, source_path, self.session)


def watch_for_photos(photos_dir: Path) -> None:
    """Will run until key is pressed"""
    logger.info("[watchdog] Watching for newly added photos!")
    event_handler = NewImageHandler()
    observer = Observer()
    observer.schedule(event_handler, str(photos_dir), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
