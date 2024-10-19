import asyncio
import logging
import sys
import time
from pathlib import Path

from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    DirCreatedEvent,
    DirDeletedEvent,
    FileDeletedEvent,
)
from watchdog.observers import Observer

from photos.config.process_config import process_config
from photos.database.database import get_session_maker
from photos.database.models import UserModel
from photos.ingest.process_image import process_image
from photos.utils import delete_image, db_path

# Need to set up logging because watchdog in different thread is weird
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
logger.addHandler(handler)


class NewImageHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        self.session = get_session_maker()()

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent) -> None:
        source_path = Path(str(event.src_path))
        if (
            not event.is_directory
            and source_path.suffix in process_config.media_suffixes
        ):
            logger.info("[watchdog] Processing new photo!")
            user_folder = db_path(source_path).parts[0]
            user = self.session.query(UserModel).filter_by(user_id=user_folder).scalar()
            asyncio.run(process_image(source_path, user, self.session))

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        source_path = Path(str(event.src_path))
        relative_path = db_path(source_path)
        delete_image(relative_path, self.session)


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
