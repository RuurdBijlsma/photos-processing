import asyncio
from pathlib import Path

from watchdog.events import (
    DirCreatedEvent,
    DirDeletedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    FileSystemEventHandler,
)

from app.config.app_config import app_config
from app.data.database.database import get_session_maker
from app.data.database.db_utils import rel_path
from app.data.database.image_operations import delete_image
from app.processing.processing.process_one import process_one


class NewMediaHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        self.session = asyncio.run(get_session_maker())()

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent) -> None:
        source_path = Path(str(event.src_path))
        if not event.is_directory and source_path.suffix in app_config.image_suffixes:
            print("[watchdog] Processing new image!")
            user_folder = rel_path(source_path).parts[0]
            asyncio.run(process_one(source_path, int(user_folder), self.session))

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        source_path = Path(str(event.src_path))
        relative_path = rel_path(source_path)
        asyncio.run(delete_image(relative_path, self.session))
