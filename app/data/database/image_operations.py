from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_config import app_config
from app.data.image_models import (
    FaceBoxModel,
    GeoLocationModel,
    ImageModel,
    ObjectBoxModel,
    OCRBoxModel,
    VisualInformationModel,
)
from app.data.interfaces.image_data import WeatherData
from app.data.interfaces.visual_data import ImageQualityData
from app.processing.processing.process_utils import clean_object


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
    image_info: WeatherData,
    visual_infos: list[ImageQualityData],
    user_id: int,
    session: AsyncSession,
) -> ImageModel:
    cleaned_dict = clean_object(image_info.model_dump())
    assert isinstance(cleaned_dict, dict)
    location = cleaned_dict.pop("location")
    location_model = None
    if location and image_info.location:
        # Check if location exists already, else create it
        location_model = (
            await session.execute(
                select(GeoLocationModel).filter_by(
                    city=image_info.location.city,
                    province=image_info.location.province,
                    country=image_info.location.country,
                ),
            )
        ).scalar()
        if not location_model:
            location_model = GeoLocationModel(**location)

    def fix_nested_visual_information(info: dict[str, Any]) -> dict[str, Any]:
        overrides = {
            "ocr_boxes": OCRBoxModel,
            "faces": FaceBoxModel,
            "objects": ObjectBoxModel,
        }
        for key, value in overrides.items():
            info[key] = [value(**item) for item in info[key]]
        return info

    image_model = ImageModel(
        **cleaned_dict,
        location=location_model,
        visual_information=[
            VisualInformationModel(**fix_nested_visual_information(info.model_dump()))
            for info in visual_infos
        ],
        user_id=user_id,
    )
    session.add(image_model)
    await session.commit()
    await session.refresh(image_model)
    return image_model
