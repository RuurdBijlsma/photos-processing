from pathlib import Path
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_config import app_config
from app.data.enums.user_role import Role
from app.data.image_models import UserModel
from app.routers.auth.auth_model import get_password_hash


def rel_path(path: Path) -> Path:
    return path.relative_to(app_config.images_dir)


def path_str(path: Path) -> str:
    return rel_path(path).as_posix()


async def add_user(
    session: AsyncSession, username: str, password: str, role: Role,
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


TK = TypeVar("TK")
TV = TypeVar("TV")


def without(dictionary: dict[TK, TV], *keys_to_remove: list[str]) -> dict[TK, TV]:
    return {key: value for key, value in dictionary.items() if
            key not in keys_to_remove}
