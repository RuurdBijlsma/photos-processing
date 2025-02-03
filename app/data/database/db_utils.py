from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_config import app_config
from app.data.enums.user_role import Role
from app.data.image_models import (
    FaceBoxModel,
    GeoLocationModel,
    ObjectBoxModel,
    OCRBoxModel,
    UserModel,
    VisualInformationModel,
)
from app.routers.auth.auth_model import get_password_hash


def rel_path(path: Path) -> Path:
    return path.relative_to(app_config.images_dir)


def path_str(path: Path) -> str:
    return rel_path(path).as_posix()


async def add_user(
    session: AsyncSession,
    username: str,
    password: str,
    role: Role,
) -> None:
    user_exists = (
        await session.execute(select(UserModel).filter_by(username=username))
    ).scalar_one_or_none()
    if user_exists:
        return
    user = UserModel(
        username=username,
        hashed_password=get_password_hash(password),
        role=role,
    )
    session.add(user)
    await session.commit()


def flatten_dataclass(
    instance: object | dict[str, Any] | list[Any] | str | float,
) -> dict[str, Any]:
    """Recursively flattens a dataclass into a dictionary, keeping original field names."""
    if not is_dataclass(instance):
        raise ValueError("Provided instance must be a dataclass")

    flattened = {}
    for key, value in instance.__dict__.items():
        if is_dataclass(value):
            flattened.update(flatten_dataclass(value))
        else:
            flattened[key] = value
    return flattened


def fix_visual_information(frame: dict[str, Any], percentage: int) -> VisualInformationModel:
    frame["faces"] = [FaceBoxModel(**asdict(f)) for f in frame["faces"]]
    frame["ocr_boxes"] = [OCRBoxModel(**asdict(f)) for f in frame["ocr_boxes"]]
    frame["objects"] = [ObjectBoxModel(**asdict(f)) for f in frame["objects"]]
    return VisualInformationModel(**frame, frame_percentage=percentage)


async def get_location_model(
    session: AsyncSession,
    image_dict: dict[str, str | float],
) -> GeoLocationModel | None:
    if "country" not in image_dict or "city" not in image_dict:
        return None

    country = image_dict.pop("country")
    province = image_dict.pop("province")
    city = image_dict.pop("city")
    latitude = image_dict.pop("place_latitude")
    longitude = image_dict.pop("place_longitude")

    location = (
        await session.execute(
            select(GeoLocationModel).filter_by(
                country=country,
                province=province,
                city=city,
            ),
        )
    ).scalar()

    if not location:
        return GeoLocationModel(
            country=country,
            province=province,
            city=city,
            latitude=latitude,
            longitude=longitude,
        )
    return location
