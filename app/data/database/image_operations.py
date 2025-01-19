from pathlib import Path

from media_analyzer.data.interfaces.api_io import MediaAnalyzerOutput
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_config import app_config
from app.data.database.db_utils import (
    fix_visual_information,
    flatten_dataclass,
    get_location_model,
    rel_path,
)
from app.data.image_models import (
    ImageModel,
)
from app.processing.processing.process_utils import hash_image


async def delete_image(relative_path: Path, session: AsyncSession) -> None:
    if relative_path.exists():
        relative_path.unlink()

    model = (
        await session.execute(
            select(ImageModel).filter_by(relative_path=relative_path.as_posix()),
        )
    ).scalar_one_or_none()

    if model is not None and model.id is not None:
        thumb_folder = app_config.thumbnails_dir / model.id
        thumb_folder.unlink(missing_ok=True)
        await session.delete(model)
        await session.commit()


async def store_image(
    analyzer_output: MediaAnalyzerOutput,
    user_id: int,
    session: AsyncSession,
) -> ImageModel:
    image_data = flatten_dataclass(analyzer_output)
    image_path = image_data.pop("path")

    if "gps" in image_data:
        image_data.pop("gps")
    if "weather" in image_data:
        image_data.pop("weather")

    image_model = ImageModel(
        relative_path=rel_path(image_path).as_posix(),
        hash=hash_image(image_path),
        filename=image_path.name,
        user_id=user_id,
        location=await get_location_model(session=session, image_dict=image_data),
        visual_information=[
            fix_visual_information(flatten_dataclass(frame), percentage)
            for frame, percentage in zip(
                image_data.pop("frame_data"),
                app_config.video_screenshot_percentages,
                strict=False,
            )
        ],
        **image_data,
    )

    session.add(image_model)
    await session.commit()
    await session.refresh(image_model)
    return image_model
