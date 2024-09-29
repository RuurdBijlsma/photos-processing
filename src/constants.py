from pathlib import Path

PHOTOS_DIR = Path("data/photos")
THUMBNAILS_DIR = Path("data/thumbnails")
THUMBNAIL_SIZES = [240, 480, 720, 1920]  # Sizes of thumbnails
CONNECTION_STRING = "postgresql://postgres:mysecretpassword@localhost:5432/photos"
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp")
