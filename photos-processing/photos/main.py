from photos.config.app_config import app_config
from photos.config.process_config import process_config
from photos.ingest.ingest_watch import process_images_in_directory, watch_for_photos

if __name__ == "__main__":
    process_images_in_directory(app_config.photos_dir, process_config)

    watch_for_photos(app_config.photos_dir, process_config)
