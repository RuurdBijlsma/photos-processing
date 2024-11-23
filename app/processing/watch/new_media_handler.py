import asyncio
from pathlib import Path

from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    DirCreatedEvent,
    DirDeletedEvent,
    FileDeletedEvent,
)

from app.config.app_config import app_config
from app.data.database.database import get_session_maker
from app.data.database.db_utils import rel_path, delete_media
from app.processing.pipelines.process_image import process_media


class NewMediaHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        self.session = asyncio.run(get_session_maker())()

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent) -> None:
        source_path = Path(str(event.src_path))
        if not event.is_directory and source_path.suffix in app_config.image_suffixes:
            print("[watchdog] Processing new image!")
            user_folder = rel_path(source_path).parts[0]
            asyncio.run(process_media(source_path, int(user_folder), self.session))

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        source_path = Path(str(event.src_path))
        relative_path = rel_path(source_path)
        asyncio.run(delete_media(relative_path, self.session))
