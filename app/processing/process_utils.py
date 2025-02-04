import hashlib
from dataclasses import dataclass
from pathlib import Path

from media_analyzer import MediaAnalyzer

from app.config.app_config import app_config

analyzer = MediaAnalyzer(config=app_config.analyzer_settings)


@dataclass
class ImageThumbnails:
    folder: Path
    thumbnails: dict[int, Path]
    frames: dict[int, Path]
    webm_videos: dict[int, Path] | None = None


def get_thumbnail_paths(image_path: Path, image_hash: str) -> ImageThumbnails:
    thumb_folder = app_config.thumbnails_dir / image_hash
    thumbnails = {
        height: thumb_folder / f"{height}p.avif" for height in app_config.thumbnail_heights
    }
    if image_path.suffix in app_config.video_suffixes:
        return ImageThumbnails(
            folder=thumb_folder,
            thumbnails=thumbnails,
            frames={
                percentage: thumb_folder / f"{percentage}_percent.avif"
                for percentage in app_config.video_screenshot_percentages
            },
            webm_videos={
                height: thumb_folder / f"{height}p.webm"
                for height, _ in app_config.web_video_height_and_quality
            },
        )
    return ImageThumbnails(
        folder=thumb_folder,
        thumbnails=thumbnails,
        frames={0: thumb_folder / f"{max(app_config.thumbnail_heights)}p.avif"},
    )


def hash_image(image_path: Path, chunk_size: int = 65536) -> str:
    hasher = hashlib.sha256()

    with image_path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)

    return hasher.hexdigest()
