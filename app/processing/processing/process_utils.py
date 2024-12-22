import hashlib
import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import PIL
from PIL.Image import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_config import app_config
from app.data.database.db_utils import path_str
from app.data.image_models import ImageModel


@dataclass
class ImageThumbnails:
    folder: Path
    thumbnails: dict[int, Path]
    frames: dict[int, Path]
    webm_videos: dict[int, Path] | None = None


def get_thumbnail_paths(image_path: Path, image_hash: str) -> ImageThumbnails:
    thumb_folder = app_config.thumbnails_dir / image_hash
    thumbnails = {height: thumb_folder / f"{height}p.avif" for height in app_config.thumbnail_heights}
    if image_path.suffix in app_config.video_suffixes:
        return ImageThumbnails(
            folder=thumb_folder,
            thumbnails=thumbnails,
            frames={
                percentage: thumb_folder / f"{percentage}_percent.avif"
                for percentage in app_config.video_screenshot_percentages
            },
            webm_videos={
                height: thumb_folder / f"{height}p.webm" for height, _ in app_config.web_video_height_and_quality
            },
        )
    return ImageThumbnails(
        folder=thumb_folder,
        thumbnails=thumbnails,
        frames={0: thumb_folder / f"{max(app_config.thumbnail_heights)}p.avif"},
    )


def pil_to_jpeg(pil_image: Image) -> Image:
    # Weird conversion to jpg so pytesseract can handle the image
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)
    jpeg_data = img_byte_arr.getvalue()
    return PIL.Image.open(io.BytesIO(jpeg_data))


def readable_bytes(num: int, suffix: str = "B") -> str:
    fnum = float(num)
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        si_unit_max = 1024.0
        if abs(fnum) < si_unit_max:
            return f"{fnum:3.1f}{unit}{suffix}"
        fnum /= 1024.0
    return f"{fnum:.1f}Yi{suffix}"


def remove_non_printable(input_string: str) -> str:
    # Use a regex to replace non-printable characters with an empty string
    return re.sub(r"[^\x20-\x7E\xA0-\uFFEF]", "", input_string)


def clean_object(obj: dict[str, Any]) -> dict[str, Any] | list[Any] | str:
    if isinstance(obj, dict):
        return {k: clean_object(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_object(v) for v in obj]
    if isinstance(obj, str):
        return remove_non_printable(obj)  # Remove non-printable characters
    return obj


async def image_needs_processing(image_path: Path, session: AsyncSession) -> bool:
    image_model = (
        await session.execute(
            select(ImageModel).filter_by(relative_path=path_str(image_path)),
        )
    ).scalar_one_or_none()
    if image_model is None:
        return True

    assert image_model.hash is not None
    # Check for each resolution
    thumbnail_paths = get_thumbnail_paths(image_path, image_model.hash)
    for thumb_path in thumbnail_paths.thumbnails.values():
        if not thumb_path.exists():
            return True

    for frame_path in thumbnail_paths.frames.values():
        if not frame_path.exists():
            return True

    if thumbnail_paths.webm_videos is not None:
        for vid in thumbnail_paths.webm_videos.values():
            if not vid.exists():
                return True

    return False


def hash_image(image_path: Path, chunk_size: int = 65536) -> str:
    hasher = hashlib.sha256()

    with image_path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)

    return hasher.hexdigest()
