import os
import time
from pathlib import Path

from tqdm import tqdm
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, DirCreatedEvent
from watchdog.observers import Observer

from photos.config.process_config import ProcessConfig
from photos.ingest.process_image import process_image


def process_images_in_directory(
        photos_dir: Path,
        process_config: ProcessConfig
) -> None:
    """Check all images for processing."""
    image_files: list[Path] = []
    for root, _, files in os.walk(photos_dir):
        for file in files:
            if file.lower().endswith(process_config.image_suffixes):
                image_files.append(Path(root) / file)

    print(f"Photos dir: {photos_dir}")
    for image_path in tqdm(image_files, desc="Processing images", unit="image"):
        process_image(photos_dir, image_path, process_config)


class NewImageHandler(FileSystemEventHandler):
    def __init__(self, photos_dir: Path, process_config: ProcessConfig):
        self.process_config = process_config
        self.photos_dir = photos_dir

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent) -> None:
        source_path = Path(str(event.src_path))
        if (
                not event.is_directory
                and source_path.suffix in self.process_config.image_suffixes
        ):
            print("Processing new photo!")
            process_image(self.photos_dir, source_path, self.process_config)


def watch_for_photos(photos_dir: Path, process_config: ProcessConfig):
    """Will run until key is pressed"""
    event_handler = NewImageHandler(photos_dir, process_config)
    observer = Observer()
    observer.schedule(event_handler, str(photos_dir), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
