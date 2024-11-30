import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pyvips  # type: ignore
from parsed_ffmpeg import run_ffmpeg, run_ffprobe
from tqdm import tqdm

from app.config.app_config import app_config
from app.processing.processing.process_utils import hash_image, ImageThumbnails, \
    get_thumbnail_paths


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
    video_height_and_quality: list[tuple[int, int]],
    thumbnails_out: ImageThumbnails,
    print_progress_bar: bool = True,
) -> None:
    """Make webm versions of video, generate thumbnails at different sizes,
        and capture screenshots at different times throughout the video."""
    if thumbnails_out.folder.exists():
        return None

    probe_result = await run_ffprobe(["ffprobe", input_path])
    assert thumbnails_out.webm_videos is not None

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        cmd: list[str | Path] = ["ffmpeg", "-y", "-i", str(input_path)]
        for height, quality in video_height_and_quality:
            cmd += [
                "-vf", f"scale=-1:{height}", "-c:v", "libvpx-vp9", "-crf", str(quality),
                "-b:v", "0", "-c:a", "libopus", "-b:a", "64k",
                file_at_temp_dir(temp_path, thumbnails_out,
                                 thumbnails_out.webm_videos[height])
            ]
        for height, thumb_path in thumbnails_out.thumbnails.items():
            cmd += [
                "-ss", "00:00:00.01", "-vf", f"scale=-1:{height}", "-frames:v", "1",
                "-crf", "35", "-b:v", "0",
                file_at_temp_dir(temp_path, thumbnails_out, thumb_path)
            ]
        for percentage, frame_path in thumbnails_out.frames.items():
            time_string = format_duration(
                int((percentage / 100) * probe_result.duration_ms)
            )
            cmd += [
                "-ss", time_string, "-vf", "scale=-1:1080", "-frames:v", "1",
                "-crf", "35", "-b:v", "0",
                file_at_temp_dir(temp_path, thumbnails_out, frame_path)
            ]
        await run_ffmpeg(
            cmd, print_progress_bar=print_progress_bar,
            progress_bar_description=input_path.name
        )
        # After ffmpeg is done, copy output from temp dir to actual thumb dir
        shutil.copytree(temp_path, thumbnails_out.folder, dirs_exist_ok=False)


async def generate_video_thumbnails(to_process: list[Path]) -> None:
    for video_path in tqdm(to_process,
            desc="Generate video thumbnails",
            unit="video"
        ):
        video_hash = hash_image(video_path)
        await generate_single_video_thumbnails(
            video_path,
            app_config.web_video_height_and_quality,
            get_thumbnail_paths(video_path, video_hash),
            print_progress_bar=False,
        )


def generate_single_photo_thumbnails(
    input_path: Path,
    thumbnails_out: ImageThumbnails
) -> None:
    if thumbnails_out.folder.exists():
        return None

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        for height, image_path in thumbnails_out.thumbnails.items():
            try:
                image = pyvips.Image.thumbnail(
                    str(input_path),
                    height * 10,
                    height=height
                )
                image.write_to_file(
                    file_at_temp_dir(temp_path, thumbnails_out, image_path),
                    Q=80,
                )
            except pyvips.Error as e:
                # todo on fail use ffmpeg, if that fails, mark photo as failed
                print(f"Error processing {input_path}, {e}")

        # After pyvips is done, copy output from temp dir to actual thumb dir
        shutil.copytree(temp_path, thumbnails_out.folder, dirs_exist_ok=False)


def generate_photo_thumbnails(to_process: list[Path]) -> None:
    # Clear lru cache of hash_image, in case old paths are cached.
    hash_image.cache_clear()
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(
                generate_single_photo_thumbnails,
                input_file,
                get_thumbnail_paths(input_file, hash_image(input_file))
            )
            for input_file in to_process
        ]
        with tqdm(
            total=len(futures),
            desc="Generate photo thumbnails",
            unit="photo"
        ) as pbar:
            for future in futures:
                future.result()
                pbar.update(1)


async def generate_generic_thumbnails(image_path: Path, image_hash: str) -> None:
    hash_image.cache_clear()
    if image_path.suffix in app_config.photo_suffixes:
        generate_single_photo_thumbnails(
            image_path,
            get_thumbnail_paths(image_path, image_hash)
        )
    elif image_path.suffix in app_config.video_suffixes:
        await generate_single_video_thumbnails(
            image_path,
            app_config.web_video_height_and_quality,
            get_thumbnail_paths(image_path, image_hash)
        )
