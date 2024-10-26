import logging
import time
from pathlib import Path

from watchdog.observers import Observer

from photos.config.app_config import app_config
from photos.processing.watch.new_media_handler import NewMediaHandler


def watch_files() -> None:
    """Will run until key is pressed"""
    print("[watchdog] Watching for newly added images!")
    event_handler = NewMediaHandler()
    observer = Observer()
    observer.schedule(event_handler, str(app_config.images_dir), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
