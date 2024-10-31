from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from photos.config.app_config import app_config
from photos.data.interfaces.image_info_types import WeatherImageInfo
from photos.data.models.image_models import ImageModel, Role, UserModel, GeoLocationModel
from photos.processing.process_utils import clean_object
from photos.server.routers.auth.auth_model import get_password_hash


def rel_path(path: Path) -> Path:
    return path.relative_to(app_config.images_dir)


def path_str(path: Path) -> str:
    return rel_path(path).as_posix()


async def delete_media(relative_path: Path, session: AsyncSession) -> None:
    if relative_path.exists():
        relative_path.unlink()

    model = (await session.execute(
        select(ImageModel).filter_by(relative_path=relative_path.as_posix())
    )).scalar_one_or_none()

    if model is not None and model.id is not None:
        thumb_folder = app_config.thumbnails_dir / model.id
        thumb_folder.unlink(missing_ok=True)
        await session.delete(model)
        await session.commit()


async def add_user(session: AsyncSession, username: str, password: str, role: Role) -> None:
    user_exists = (await session.execute(
        select(UserModel).filter_by(username=username)
    )).scalar_one_or_none()
    if user_exists:
        return
    admin = UserModel(
        username=username,
        hashed_password=get_password_hash(password),
        role=role,
    )
    session.add(admin)
    await session.commit()


async def store_image(
    image_info: WeatherImageInfo,
    user_id: int,
    session: AsyncSession
) -> ImageModel:
    cleaned_dict = clean_object(image_info.model_dump())
    assert isinstance(cleaned_dict, dict)
    location = cleaned_dict.pop("location")
    location_model = None
    if location and image_info.location:
        location_model = (await session.execute(
            select(GeoLocationModel)
            .filter_by(
                city=image_info.location.city,
                province=image_info.location.province,
                country=image_info.location.country,
            )
        )).scalar()
        if not location_model:
            location_model = GeoLocationModel(**location)
    image_model = ImageModel(**cleaned_dict, location=location_model, user_id=user_id)
    session.add(image_model)
    await session.commit()
    await session.refresh(image_model)
    return image_model
