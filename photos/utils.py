import re
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from photos.config.app_config import app_config
from photos.config.process_config import process_config
from photos.database.database import get_session_maker
from photos.database.models import ImageModel, UserModel, Role
from photos.routers.auth import get_password_hash


def path_str(path: Path) -> str:
    return db_path(path).as_posix()


def db_path(path: Path) -> Path:
    return path.relative_to(app_config.photos_dir)


def readable_bytes(num: int, suffix: str = "B") -> str:
    fnum = float(num)
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(fnum) < 1024.0:
            return f"{fnum:3.1f}{unit}{suffix}"
        fnum /= 1024.0
    return f"{fnum:.1f}Yi{suffix}"


def delete_image(relative_path: Path, session: Session) -> None:
    if relative_path.exists():
        relative_path.unlink()
    model = (
        session.query(ImageModel)
        .filter(ImageModel.relative_path.__eq__(relative_path.as_posix()))
        .first()
    )
    if model is not None and model.id is not None:
        thumb_folder = process_config.thumbnails_dir / model.id
        thumb_folder.unlink(missing_ok=True)
        session.delete(model)
        session.commit()


def add_user(username: str, password: str, role: Role) -> None:
    session = get_session_maker()()
    existing_admin = session.query(UserModel).filter_by(username=username).first()
    if existing_admin:
        return
    admin = UserModel(
        username=username,
        hashed_password=get_password_hash(password),
        role=role,
    )
    session.add(admin)
    session.commit()


def remove_non_printable(input_string: str) -> str:
    # Use a regex to replace non-printable characters with an empty string
    return re.sub(r"[^\x20-\x7E\xA0-\uFFEF]", "", input_string)


def clean_object(obj: dict[str, Any]) -> dict[str, Any] | list[Any] | str:
    if isinstance(obj, dict):
        return {k: clean_object(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_object(v) for v in obj]
    elif isinstance(obj, str):
        return remove_non_printable(obj)  # Remove non-printable characters
    else:
        return obj
