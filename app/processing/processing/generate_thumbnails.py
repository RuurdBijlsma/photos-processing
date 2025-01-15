import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pyvips
from parsed_ffmpeg import FfmpegError, run_ffmpeg, run_ffprobe
from tqdm import tqdm

from app.config.app_config import app_config
from app.processing.processing.process_utils import (
    ImageThumbnails,
    get_thumbnail_paths,
    hash_image,
)


def file_at_temp_dir(
    temp_path: Path,
    thumbnails_out: ImageThumbnails,
    out_path: Path,
) -> Path:
    relative_path = out_path.relative_to(thumbnails_out.folder)
    return temp_path / relative_path


def format_duration(milliseconds: int) -> str:
    total_seconds = milliseconds // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    centiseconds = (milliseconds % 1000) // 10
    return f"{hours:02}:{minutes:02}:{seconds:02}.{centiseconds:02}"


async def generate_single_video_thumbnails(
    input_path: Path,
    video_height_and_quality: tuple[tuple[int, int], ...],
    thumbnails_out: ImageThumbnails,
    print_progress_bar: bool = True,
) -> bool:
    """Make webm versions of video, generate thumbnails at different sizes,
    and capture screenshots at different times throughout the video.
    """
    if thumbnails_out.folder.exists():
        return True

    try:
        probe_result = await run_ffprobe(["ffprobe", input_path])
    except FfmpegError as e:
        print(f"Failed to process (probe) video.\n\n{e}")
        return False
    assert thumbnails_out.webm_videos is not None

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        cmd: list[str | Path] = ["ffmpeg", "-y", "-i", str(input_path)]
        for height, quality in video_height_and_quality:
            cmd += [
                "-vf",
                f"scale=-1:{height}",
                "-c:v",
                "libvpx-vp9",
                "-crf",
                str(quality),
                "-b:v",
                "0",
                "-c:a",
                "libopus",
                "-b:a",
                "64k",
                file_at_temp_dir(temp_path, thumbnails_out, thumbnails_out.webm_videos[height]),
            ]
        for height, thumb_path in thumbnails_out.thumbnails.items():
            cmd += [
                "-ss",
                "00:00:00.01",
                "-vf",
                f"scale=-1:{height}",
                "-frames:v",
                "1",
                "-crf",
                "35",
                "-b:v",
                "0",
                file_at_temp_dir(temp_path, thumbnails_out, thumb_path),
            ]
        for percentage, frame_path in thumbnails_out.frames.items():
            time_string = format_duration(
                int((percentage / 100) * probe_result.duration_ms),
            )
            cmd += [
                "-ss",
                time_string,
                "-vf",
                "scale=-1:1080",
                "-frames:v",
                "1",
                "-crf",
                "35",
                "-b:v",
                "0",
                file_at_temp_dir(temp_path, thumbnails_out, frame_path),
            ]
        try:
            await run_ffmpeg(
                cmd,
                print_progress_bar=print_progress_bar,
                progress_bar_description=input_path.name,
                progress_bar_leave=False,
                progress_bar_position=1,
            )
        except FfmpegError as e:
            print(f"Failed to process (convert) video.\n\n{e}")
            return False
        # After ffmpeg is done, copy output from temp dir to actual thumb dir
        shutil.copytree(temp_path, thumbnails_out.folder, dirs_exist_ok=False)
    return True


async def generate_video_thumbnails(to_process: list[Path]) -> list[bool]:
    results: list[bool] = []
    for video_path in tqdm(
        to_process,
        desc="Generate video thumbnails",
        unit="video",
        position=0,
    ):
        video_hash = hash_image(video_path)
        results.append(
            await generate_single_video_thumbnails(
                video_path,
                app_config.web_video_height_and_quality,
                get_thumbnail_paths(video_path, video_hash),
                print_progress_bar=True,
            ),
        )
    return results


def generate_single_photo_thumbnails(
    input_path: Path,
    thumbnails_out: ImageThumbnails,
) -> bool:
    if thumbnails_out.folder.exists():
        return True

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        for height, image_path in thumbnails_out.thumbnails.items():
            try:
                image = pyvips.Image.thumbnail(
                    str(input_path),
                    height * 10,
                    height=height,
                )
                image.write_to_file(
                    file_at_temp_dir(temp_path, thumbnails_out, image_path),
                    Q=80,
                )
            except pyvips.Error as e:
                print(f"pyvips.Error processing {input_path}, {e}")
                return False

        # After pyvips is done, copy output from temp dir to actual thumb dir
        shutil.copytree(temp_path, thumbnails_out.folder, dirs_exist_ok=False)
    return True


def generate_photo_thumbnails(to_process: list[Path]) -> list[bool]:
    with ThreadPoolExecutor(max_workers=8) as executor:
        return list(
            tqdm(
                executor.map(
                    lambda file: generate_single_photo_thumbnails(
                        file,
                        get_thumbnail_paths(file, hash_image(file)),
                    ),
                    to_process,
                ),
                total=len(to_process),
                desc="Generate photo thumbnails",
                unit="photo",
            ),
        )


async def generate_generic_thumbnails(image_path: Path, image_hash: str) -> bool:
    if image_path.suffix in app_config.photo_suffixes:
        return generate_single_photo_thumbnails(
            image_path,
            get_thumbnail_paths(image_path, image_hash),
        )
    if image_path.suffix in app_config.video_suffixes:
        return await generate_single_video_thumbnails(
            image_path,
            app_config.web_video_height_and_quality,
            get_thumbnail_paths(image_path, image_hash),
        )
    return False
